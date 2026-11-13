# Guide GitHub Pages chung cho Lucky Studio

## Nơi dùng chung

- Local: `/Users/fkr.onsiter/lucky/lucky-studio-pages`.
- GitHub: `https://github.com/vnluckystudio/lucky-studio-pages`.
- Base URL dự kiến: `https://vnluckystudio.github.io/lucky-studio-pages/`.
- Registry nguồn: `content/apps.json`. HTML sinh tự động: `docs/`.
- Skill được cài tại `~/.codex/skills/lucky-studio-pages`, trỏ về `skills/lucky-studio-pages` trong repo này.

Áp dụng cho mọi app hiện tại và tương lai trong `lucky`, kể cả app con trong monorepo. Không tạo thêm repo Pages riêng cho app mới nếu không có yêu cầu khác của người dùng. Website này dành cho thông tin công khai và tài liệu; game runtime, backend, OTA và tài nguyên nặng tiếp tục dùng kênh riêng của app.

## Thêm hoặc cập nhật một app

1. Đọc AGENTS.md ở gốc `lucky` và tài liệu của app. Xác minh tên công khai, bundle ID/app ID, nền tảng, thông tin liên hệ và thực tế SDK/data practices. Dùng owner `Lucky Studio`, số `+821083312512`. Không suy diễn tên seller từ tài khoản đăng nhập.
2. Thêm object vào `content/apps.json`; dùng ID ổn định, ưu tiên bundle ID chữ thường. Giữ nguyên ID khi đổi tên hiển thị. Không tự liệt kê toàn bộ thư mục nội bộ thành app công khai.
3. Thêm privacy/terms chỉ khi có nội dung đã xác minh cho app đó. Thiếu thông tin thiết yếu thì hỏi trước khi công khai chính sách hay gửi hồ sơ store. Không sao chép lời khẳng định về dữ liệu của app khác.
4. Build và kiểm tra cục bộ bằng các lệnh bên dưới. Kiểm tra trang app, support, privacy/terms có mặt, và link chạy đúng dưới prefix `/lucky-studio-pages/`.
5. Chỉ stage file thuộc task, xem diff trước commit. Kiểm tra Pages và workflow hiện hành trước push: nếu push sẽ trigger Actions, cần yêu cầu chạy Actions rõ ràng từ người dùng. Không tự dispatch/rerun, gọi Pages build API, bật Pages hoặc thêm auto workflow để đi vòng quy tắc này.
6. Khi đã được yêu cầu publish có chạy Actions, deploy và kiểm tra URL trả HTTP 200 cùng đúng nội dung mới. Chỉ sau đó mới dùng URL live trong metadata/app. Không tự sửa hay submit App Store Connect khi task chỉ làm website.

Ví dụ registry cho trang giới thiệu và support (thay toàn bộ giá trị mẫu bằng dữ liệu thật trước khi thêm):

```json
[
  {
    "id": "com.example.app",
    "name": "App Display Name",
    "platform": "iOS",
    "summary": "Verified public description."
  }
]
```

Hai trường tùy chọn `privacy` và `terms` dùng cùng cấu trúc: `{"updated":"YYYY-MM-DD","sections":[["Heading","Reviewed paragraph."]]}`. Mỗi section gồm tiêu đề và ít nhất một đoạn văn bản thuần; generator tạo anchor từ tiêu đề để app có thể liên kết trực tiếp đến một mục chính sách. Trường tùy chọn `support_email` thêm địa chỉ email vào trang hỗ trợ của app. Generator escape HTML; không chèn script hay HTML vào registry. Ngày `updated` phải là ngày sửa nội dung thật.

## URL của từng app

Thay `<id>` bằng ID trong registry:

| Mục đích | Đường dẫn sau base URL |
| --- | --- |
| Marketing / giới thiệu | `apps/<id>/` |
| Support | `apps/<id>/support/` |
| Privacy Policy | `apps/<id>/privacy/` |
| Terms | `apps/<id>/terms/` |

Privacy/terms chỉ tồn tại khi có nội dung tương ứng. Repo có `support/` dùng chung. Link bên trong website dùng đường dẫn tương đối; không bỏ prefix project khi dùng URL tuyệt đối. Không dùng URL dự kiến để khai hồ sơ trước khi trang thực sự live.

## Build, preview, publish

Chạy từ thư mục repo, chỉ cần Python 3, không cài dependency:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m http.server 8789 --directory docs
```

Mở `http://localhost:8789/`, dừng server sau QA. Để kiểm tra prefix thật, serve thư mục cha và mở `/lucky-studio-pages/docs/`. Trang 404 dùng prefix production.

Khi người dùng đã yêu cầu rõ chạy Actions để publish: trong Settings → Pages, chọn **Deploy from a branch**, branch **main**, folder **/docs**. Không cần custom workflow. Có thể cấu hình tương đương bằng GitHub Pages API. GitHub vẫn chạy workflow deploy của hệ thống. Xác minh trạng thái deploy và các URL live; không báo đã publish chỉ vì đã push.

Trước khi publish lần đầu, Pages đang chưa bật và repo không có workflow. Sau khi bật, mọi push vào source branch có thể khởi chạy deploy; những lần sau cũng phải tuân thủ quy tắc Actions của người dùng. Khi không được phép chạy, hoàn thiện local commit rồi báo phần publish còn chờ.

## Chuyển các trang cũ

`lucky-studio-policies`, các repo legal/privacy cũ và hosting Sites hiện có giữ nguyên. Chưa có app nào được chuyển chỉ vì tạo repo chung. Khi chuyển một app: xác minh nội dung nguồn, tạo các trang mới, publish và kiểm tra, rồi mới đổi URL trong app/store theo phạm vi được giao. Giữ URL cũ phục vụ nội dung hoặc redirect rõ ràng, không xóa nguồn cũ. Không đổi bundle ID để đổi URL. Generator chặn việc vô tình bỏ route cũ; cần lập phương án redirect riêng nếu thực sự thay route.

## Vận hành và hiệu quả

Mục tiêu: một repo và quy trình cho mọi app, giảm việc tạo hosting lặp lại, giữ URL ổn định. Chi phí hạ tầng dự kiến là $0 với public repo trong GitHub Free và quota Pages; không mua domain hoặc dịch vụ trả phí trong thiết lập này. Chỉ chứa thông tin công khai: không certificate, provisioning profile, tài khoản review, token, dữ liệu người dùng hoặc IPA. Theo dõi thời gian thêm app, số link hỏng và công sức bảo trì để đánh giá hiệu quả; không hứa hẹn doanh thu.

GitHub Pages không chạy backend; site tối đa 1 GB và có soft bandwidth limit 100 GB/tháng. Đánh giá hosting riêng nếu nhu cầu vượt phạm vi website thông tin.

Nguồn kiểm tra ngày 2026-11-13:

- [Cấu hình nguồn publish và Actions của Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
- [Giới hạn Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).
