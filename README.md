# Lucky Studio Pages

Repo GitHub Pages dùng chung cho trang giới thiệu, support, privacy và terms của tất cả game/app Lucky Studio. Đây là website tĩnh, không chứa source game, backend hoặc bản cài đặt.

- Repo: https://github.com/vnluckystudio/lucky-studio-pages
- URL dự kiến sau khi bật Pages: https://vnluckystudio.github.io/lucky-studio-pages/
- Owner/seller: **Lucky Studio**. Liên hệ: **+821083312512**.
- Quy trình đầy đủ: [GUIDE.md](GUIDE.md).
- Skill: [skills/lucky-studio-pages/SKILL.md](skills/lucky-studio-pages/SKILL.md).

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m http.server 8789 --directory docs
```

Chỉ `docs/` là nội dung deploy. `content/apps.json` là registry các app đã được xác minh để công khai. Hiện có nội dung Leaf & Flutter được chuẩn bị tại đường dẫn ổn định `apps/com.vn.lucky.studio.sauanla/`; các URL của site này chỉ là dự kiến cho đến khi Pages được publish và kiểm tra. Chính sách và support cũ vẫn được giữ nguyên trong thời gian chờ migration.

Publish dự kiến từ branch `main`, thư mục `/docs`. Chưa bật Pages trong lần khởi tạo: GitHub Pages luôn cần một Actions run, kể cả deploy từ branch. Chỉ bật hoặc trigger khi người dùng yêu cầu rõ. Không có custom workflow tự chạy trong repo.
