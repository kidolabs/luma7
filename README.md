# Reading for Vocabulary — Reader (A · B · C · D)

Bản đọc offline của bộ **Reading for Vocabulary** (WorldCom Edu), 4 cuốn A/B/C/D.
Mỗi cuốn chỉ giữ **Word List + Reading** (bỏ Exercise), kèm **audio gốc** của nhà
xuất bản, gắn vào player bar phát trực tiếp — không cần quét QR.

## Mở
- Mở `index.html` (tủ sách) → chọn cuốn để đọc.
- Mỗi cuốn: nav theo **Unit**, nút **🔊 Nghe** nạp vào player bar dưới đáy
  (prev/next/seek/tốc độ/đóng, tự chuyển bài), nút ẩn/hiện thanh trên.

## Cấu trúc
```
index.html            # tủ sách (landing)
covers/               # bìa 4 cuốn (worldcomedu)
level-a|b|c|d/
  index.html          # reader
  pages/*.jpg         # ảnh trang (render từ PDF, đúng chiều)
  audio/*.mp3         # audio gốc NXB
  source.pdf          # PDF gốc
  spec.json           # map lesson → trang + audio
_build/               # script tái tạo + dữ liệu TOC/spans
```

| Cuốn | Units | Lessons | Audio |
|------|-------|---------|-------|
| A | 7 | 14 | 28 |
| B | 5 | 15 | 30 |
| C | 5 | 15 | 30 |
| D | 5 | 15 | 30 |

Nội dung thuộc bản quyền WorldCom Edu — repo dùng cá nhân, để **private**.
