SERVICES=("nginx" "ssh")

for SERVICE in "${SERVICES[@]}"; do
    STATUS=$(systemctl is-active "$SERVICE" 2>/dev/null)
    
    if [ "$STATUS" == "active" ]; then
        echo -e "[OK] Dịch vụ $SERVICE${NC} đang chạy bình thường."
    else
        echo -e "[CẢNH BÁO] Dịch vụ $SERVICE ĐÃ CHẾT (Trạng thái: $STATUS)!${NC}"
    fi
done
