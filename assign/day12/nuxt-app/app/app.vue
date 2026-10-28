<script setup lang="ts">
useHead({ title: 'Day 12 - Nuxt on S3 + CloudFront' })
const count = ref(0)
</script>

<template>
  <main class="wrap">
    <h1>Day 12 - Nuxt.js trên S3 + CloudFront</h1>
    <p>Trang web tĩnh build bằng <b>nuxt generate</b>, lưu trên <b>S3</b>, phân phối qua <b>CloudFront</b>.</p>

    <div class="card">
      <p>Bấm thử để kiểm tra Vue đang chạy:</p>
      <button @click="count++">Đã bấm {{ count }} lần</button>
    </div>

    <ul>
      <li>S3 bucket: chặn public, chỉ CloudFront đọc được (OAC)</li>
      <li>CloudFront: HTTPS, cache ở edge gần người dùng</li>
    </ul>
  </main>
</template>

<style>
body { margin: 0; font-family: system-ui, sans-serif; background: #f4f6f8; color: #222; }
.wrap { max-width: 720px; margin: 60px auto; padding: 0 16px; }
h1 { color: #00a865; }
.card { background: #fff; padding: 20px; border-radius: 12px; margin: 24px 0; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
button { background: #00a865; color: #fff; border: 0; padding: 10px 18px; border-radius: 8px; font-size: 16px; cursor: pointer; }
</style>