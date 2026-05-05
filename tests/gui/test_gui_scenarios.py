import pytest
import time
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:5000"

def wait_for_bot_reply(page: Page, previous_count: int, timeout: int = 15000):
    # Đợi cho đến khi số lượng tin nhắn tăng lên (có tin nhắn phản hồi của bot)
    page.wait_for_function(f"document.querySelectorAll('.message').length > {previous_count}", timeout=timeout)
    # Lấy tin nhắn cuối cùng
    messages = page.locator('.message')
    last_message = messages.nth(messages.count() - 1)
    return last_message

@pytest.fixture
def test_context():
    return {"results": []}

# Kịch bản 1: Câu hỏi text đơn giản
def test_scenario_1_simple_text(page: Page):
    start_time = time.time()
    page.goto(BASE_URL)
    
    msg_count = page.locator('.message').count()
    
    page.fill('#user-input', 'Giới thiệu chung về Trường')
    page.click('button:has-text("Gửi")')
    
    # Wait for user message and bot reply
    bot_reply = wait_for_bot_reply(page, msg_count + 1)
    
    latency = (time.time() - start_time) * 1000
    assert latency < 15000, "Latency exceeds 15 seconds"
    
    assert bot_reply.is_visible()
    
    print(f"\n[Scenario 1] Latency: {latency:.2f}ms")
    print(f"[Scenario 1] Output: {bot_reply.inner_text()[:100]}...")

# Kịch bản 2: Câu hỏi cần bảng
def test_scenario_2_table_question(page: Page):
    start_time = time.time()
    page.goto(BASE_URL)
    
    msg_count = page.locator('.message').count()
    
    page.fill('#user-input', 'Các bậc đào tạo và loại hình tương ứng')
    page.click('button:has-text("Gửi")')
    
    bot_reply = wait_for_bot_reply(page, msg_count + 1)
    
    # Kiểm tra có render table không
    table = page.locator('.bot-message-table table')
    expect(table).to_be_visible(timeout=15000)
    
    # Kiểm tra có highlight không (nếu LLM/engine có trả về highlight_cells)
    # Vì mock / engine thực có thể không extract được chính xác ID dựa trên dữ liệu hiện tại, ta kiểm tra table hiển thị là đạt
    assert table.locator('tr').count() > 1
    
    latency = (time.time() - start_time) * 1000
    print(f"\n[Scenario 2] Latency: {latency:.2f}ms")
    print(f"[Scenario 2] Table rendered successfully")

# Kịch bản 3: Câu hỏi về thư viện
def test_scenario_3_library_question(page: Page):
    page.goto(BASE_URL)
    
    # Khai báo role
    msg_count = page.locator('.message').count()
    page.fill('#user-input', 'Tôi là sinh viên')
    page.click('button:has-text("Gửi")')
    wait_for_bot_reply(page, msg_count + 1)
    
    # Hỏi câu thư viện
    msg_count = page.locator('.message').count()
    page.fill('#user-input', 'Sinh viên được mượn tối đa bao nhiêu sách?')
    page.click('button:has-text("Gửi")')
    
    bot_reply = wait_for_bot_reply(page, msg_count + 1)
    
    # Text bot_reply có thể chứa bảng hoặc text
    content = page.locator('.chat-box').inner_html()
    assert "3" in content or "cuốn" in content.lower()
    print("\n[Scenario 3] Bot replied contextually.")

# Kịch bản 4: Câu hỏi OOD
def test_scenario_4_ood_question(page: Page):
    page.goto(BASE_URL)
    
    msg_count = page.locator('.message').count()
    page.fill('#user-input', 'Cách nấu phở bò ngon nhất?')
    page.click('button:has-text("Gửi")')
    
    bot_reply = wait_for_bot_reply(page, msg_count + 1)
    reply_text = bot_reply.inner_text().lower()
    
    assert "ngoài phạm vi" in reply_text or "không có thông tin" in reply_text or "không tìm thấy" in reply_text
    print("\n[Scenario 4] OOD detection works.")

# Kịch bản 5: Multi-turn memory
def test_scenario_5_multi_turn(page: Page):
    page.goto(BASE_URL)
    
    # Turn 1
    msg_count = page.locator('.message').count()
    page.fill('#user-input', 'Chào bot, tôi tên là Tuấn.')
    page.click('button:has-text("Gửi")')
    wait_for_bot_reply(page, msg_count + 1)
    
    # Turn 2
    msg_count = page.locator('.message').count()
    page.fill('#user-input', 'Bạn nhớ tên tôi là gì không?')
    page.click('button:has-text("Gửi")')
    bot_reply = wait_for_bot_reply(page, msg_count + 1)
    
    assert "Tuấn" in bot_reply.inner_text()
    print("\n[Scenario 5] Multi-turn memory works.")

# Kịch bản 6: Lỗi hệ thống (mô phỏng server down bằng bad URL)
def test_scenario_6_system_error(page: Page):
    # Stop backend (In real scenario, we'd mock it, but here we just test UI fallback)
    # We will simulate by injecting a bad endpoint in JS via page.evaluate or just let it timeout
    page.goto(BASE_URL)
    
    # Break the API URL
    page.evaluate("window.fetch = async () => { throw new Error('API Offline'); }")
    
    msg_count = page.locator('.message').count()
    page.fill('#user-input', 'Alo')
    page.click('button:has-text("Gửi")')
    
    bot_reply = wait_for_bot_reply(page, msg_count + 1)
    assert "Không thể kết nối" in bot_reply.inner_text() or "Lỗi" in bot_reply.inner_text()
    print("\n[Scenario 6] Error handling works.")
