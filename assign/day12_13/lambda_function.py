import json
import os
from decimal import Decimal

import boto3

# Tên bảng lấy từ biến môi trường, không ghi cứng trong code
TABLE_NAME = os.environ["TABLE_NAME"]
table = boto3.resource("dynamodb").Table(TABLE_NAME)


def to_json(value):
    # DynamoDB trả số dạng Decimal, json không đọc được nên đổi sang int/float
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError(f"Cannot serialize {type(value)}")


def lambda_handler(event, context):
    # Scan: đọc toàn bộ bảng (bảng nhỏ nên dùng được)
    response = table.scan()
    users = response.get("Items", [])

    # Bảng lớn thì DynamoDB trả nhiều trang, đọc tiếp cho hết
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        users.extend(response.get("Items", []))

    users.sort(key=lambda u: u["id"])

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {"count": len(users), "users": users},
            default=to_json,
            ensure_ascii=False,
        ),
    }
