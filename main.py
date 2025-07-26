from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import shutil
import webbrowser

# 配置常量
COOKIE_FILE = "youtube_cookies.json"
DEFAULT_VIDEO_URL = "https://youtu.be/_wqlHmhCqug?si=IhySzXenMXA2IR_0"

def save_cookies(driver):
    """
    保存当前浏览器的cookies到文件
    """
    try:
        cookies = driver.get_cookies()
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        print(f"✅ Cookies已保存到 {COOKIE_FILE}")
        return True
    except Exception as e:
        print(f"❌ 保存cookies失败: {e}")
        return False

def load_cookies(driver):
    """
    从文件加载cookies到浏览器
    """
    try:
        if not os.path.exists(COOKIE_FILE):
            print("📝 未找到已保存的cookies文件")
            return False
        
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        # 先访问YouTube主页才能设置cookies
        driver.get("https://www.youtube.com")
        time.sleep(2)
        
        # 添加所有cookies
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"⚠️ 添加cookie失败: {e}")
        
        print("✅ Cookies已加载")
        return True
    except Exception as e:
        print(f"❌ 加载cookies失败: {e}")
        return False

def check_login_status(driver):
    """
    检查是否已登录YouTube
    """
    try:
        # 查找登录状态标识
        driver.get("https://www.youtube.com")
        time.sleep(3)
        
        # 检查是否有用户头像或登录按钮
        try:
            # 查找用户头像按钮
            avatar = driver.find_element(By.CSS_SELECTOR, "#avatar-btn")
            print("✅ 检测到已登录状态")
            return True
        except:
            # 查找登录按钮
            try:
                sign_in = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Sign in')]")
                print("❌ 未登录状态")
                return False
            except:
                print("⚠️ 无法确定登录状态")
                return False
    except Exception as e:
        print(f"❌ 检查登录状态失败: {e}")
        return False

def youtube_login(driver):
    """
    引导用户登录YouTube
    """
    print("\n🔐 开始YouTube登录流程...")
    print("选择登录方式:")
    print("1. 直接在YouTube页面登录 (推荐)")
    print("2. 通过Google登录页面")
    
    login_method = input("请选择登录方式 (1/2): ").strip()
    
    if login_method == "2":
        # 原来的Google登录页面方式
        print("请在浏览器中手动完成以下步骤:")
        print("1. 点击右上角的'登录'按钮")
        print("2. 输入您的Google账号和密码")
        print("3. 完成任何二步验证")
        print("4. 确认登录成功后，回到此程序")
        
        driver.get("https://accounts.google.com/signin/v2/identifier?service=youtube")
    else:
        # 推荐的YouTube直接登录方式
        print("📺 正在打开YouTube，请按以下步骤登录:")
        print("1. 等待页面加载完成")
        print("2. 点击右上角的'登录'按钮")
        print("3. 在弹出的窗口中输入您的Google账号和密码")
        print("4. 完成任何二步验证（如果需要）")
        print("5. 确认登录成功后，回到此程序")
        
        # 先访问YouTube主页
        driver.get("https://www.youtube.com")
        time.sleep(3)
        
        # 尝试自动点击登录按钮
        try:
            sign_in_btn = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Sign in')]")
            print("🖱️ 找到登录按钮，正在自动点击...")
            sign_in_btn.click()
            time.sleep(2)
        except:
            print("⚠️ 未找到登录按钮，请手动点击右上角的登录按钮")
    
    # 等待用户完成登录
    input("\n✋ 请在浏览器中完成登录，然后按Enter键继续...")
    
    # 验证登录状态
    if check_login_status(driver):
        print("🎉 登录成功！")
        save_cookies(driver)
        return True
    else:
        print("❌ 登录验证失败")
        print("\n💡 如果遇到'This browser or app may not be secure'错误:")
        print("1. 尝试使用YouTube页面直接登录")
        print("2. 在Google账户设置中开启'不够安全的应用的访问权限'")
        print("3. 或者选择跳过登录，以访客模式观看视频")
        return False

def setup_chrome_options():
    """
    设置Chrome选项，简化配置
    """
    chrome_options = Options()
    
    # 基本设置
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 设置用户数据目录
    user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # 减少日志输出
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-logging")
    
    # 设置用户代理
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"--user-agent={user_agent}")
    
    # 浏览器偏好设置
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "popups": 0,
        }
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options
def execute_stealth_script(driver):
    """
    执行简化的反检测脚本
    """
    stealth_js = """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """
    driver.execute_script(stealth_js)

def handle_login_flow(driver):
    """
    处理登录流程
    """
    has_saved_cookies = os.path.exists(COOKIE_FILE)
    logged_in = False
    
    if has_saved_cookies:
        print("📂 发现已保存的登录信息")
        use_saved_login = input("🔑 是否使用已保存的登录状态? (y/n): ").lower().strip()
        
        if use_saved_login == 'y':
            print("📂 正在加载已保存的cookies...")
            if load_cookies(driver):
                print("🔄 正在验证登录状态...")
                driver.refresh()
                time.sleep(3)
                logged_in = check_login_status(driver)
                if logged_in:
                    print("🎉 登录状态验证成功！")
                else:
                    print("⚠️ 已保存的登录状态已过期")
    
    if not logged_in:
        print("选择登录方式:")
        print("1. 登录YouTube账号 (推荐)")
        print("2. 跳过登录，直接观看视频")
        login_choice = input("请选择 (1/2): ").strip()
        
        if login_choice == '1':
            logged_in = youtube_login(driver)
        else:
            print("🌐 将以访客模式打开视频")
    
    return logged_in

def open_youtube_with_login():
    """
    打开YouTube并支持登录功能
    """
    chrome_options = setup_chrome_options()
    
    try:
        print("🚀 正在启动Chrome浏览器...")
        print("⏳ 请稍等，浏览器正在初始化...")
        
        # 创建WebDriver实例
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 执行反检测脚本
        execute_stealth_script(driver)
        driver.set_window_size(1920, 1080)
        
        print("✅ Chrome浏览器已启动完成！")
        print("=" * 50)
        
        # 处理登录流程
        logged_in = handle_login_flow(driver)
        
        # 打开YouTube视频
        print(f"\n🎥 正在打开YouTube视频...")
        print(f"🔗 链接: {DEFAULT_VIDEO_URL}")
        print("⏳ 请稍等，正在加载视频页面...")
        
        driver.get(DEFAULT_VIDEO_URL)
        time.sleep(5)
        
        # 尝试点击播放按钮
        try:
            play_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-large-play-button"))
            )
            play_button.click()
            print("▶️ 已自动点击播放按钮")
        except:
            print("ℹ️ 视频已自动播放或无需手动点击")
        
        print("\n" + "=" * 50)
        print("✅ YouTube视频已成功打开！")
        if logged_in:
            print("🔐 已登录状态：可访问个人内容和获得个性化推荐")
        else:
            print("🌐 访客模式：可正常观看视频")
        
        print("\n💡 使用提示:")
        print("- 您可以在浏览器中正常使用所有YouTube功能")
        print("- 如果登录了，状态将自动保存到下次使用")
        print("- 观看完毕后，回到此窗口按Enter键关闭")
        print("=" * 50)
        print("⏸️ 按Enter键关闭浏览器...")
        
        input()  # 等待用户输入
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查网络连接是否正常")
        print("2. 确保Chrome浏览器已正确安装")
        print("3. 关闭其他Chrome窗口后重试")
        print("4. 重启程序或重启计算机")
        input("按Enter键退出...")
        
    finally:
        # 在关闭前再次保存cookies（如果已登录）
        if 'driver' in locals():
            try:
                if check_login_status(driver):
                    save_cookies(driver)
                    print("💾 登录状态已保存")
            except:
                pass
            driver.quit()
            print("🔒 浏览器已关闭")

def clear_saved_data():
    """
    清除保存的cookies和用户数据
    """
    try:
        # 删除cookies文件
        if os.path.exists(COOKIE_FILE):
            os.remove(COOKIE_FILE)
            print("✅ 已清除保存的cookies")
        
        # 删除Chrome用户数据目录
        user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
            print("✅ 已清除Chrome用户数据")
        
        print("🔄 所有保存的数据已清除")
    except Exception as e:
        print(f"❌ 清除数据时发生错误: {e}")

def open_youtube_alternative():
    """
    替代方案：使用默认浏览器打开YouTube
    """
    print(f"🌐 使用默认浏览器打开YouTube视频: {DEFAULT_VIDEO_URL}")
    webbrowser.open(DEFAULT_VIDEO_URL)
    print("✅ 视频已在默认浏览器中打开")

def troubleshoot_login_issues():
    """
    登录问题故障排除指南
    """
    print("\n" + "=" * 60)
    print("🛠️  YouTube登录问题故障排除指南")
    print("=" * 60)
    
    print("\n❌ 遇到 'This browser or app may not be secure' 错误？")
    print("\n🔧 解决方案 (按顺序尝试):")
    
    print("\n1️⃣ 方法一：允许不够安全的应用访问")
    print("   📱 步骤：")
    print("   • 访问: https://myaccount.google.com/security")
    print("   • 找到 '不够安全的应用的访问权限'")
    print("   • 开启该选项")
    print("   • 重新运行程序")
    
    print("\n2️⃣ 方法二：使用应用专用密码")
    print("   🔐 步骤：")
    print("   • 确保已开启两步验证")
    print("   • 访问: https://myaccount.google.com/apppasswords")
    print("   • 生成一个应用专用密码")
    print("   • 使用该密码代替普通密码登录")
    
    print("\n3️⃣ 方法三：手动打开浏览器")
    print("   🌐 步骤：")
    print("   • 正常打开Chrome浏览器")
    print("   • 手动登录YouTube")
    print("   • 保持浏览器开启")
    print("   • 运行程序时选择选项2（默认浏览器）")
    
    print("\n4️⃣ 方法四：无登录模式")
    print("   👤 直接以访客身份观看视频")
    print("   • 虽然无法访问个人内容")
    print("   • 但所有公开视频都可以正常观看")
    
    print("\n💡 其他建议:")
    print("   • 确保网络连接稳定")
    print("   • 关闭VPN或代理")
    print("   • 清除浏览器缓存")
    print("   • 更新Chrome到最新版本")
    
    print("\n" + "=" * 60)
    input("📖 阅读完成后按Enter键返回主菜单...")

if __name__ == "__main__":
    print("🎬 YouTube视频播放器 v2.1 - 增强版")
    print("=" * 50)
    print("选择功能:")
    print("1. 🔐 使用Selenium WebDriver（支持登录和cookie保存）")
    print("2. 🌐 使用默认浏览器（简单快速）")
    print("3. 🗑️ 清除保存的登录数据")
    print("4. 🛠️ 登录问题故障排除指南")
    print("=" * 50)
    
    choice = input("请输入选择 (1/2/3/4): ").strip()
    
    if choice == "2":
        open_youtube_alternative()
    elif choice == "3":
        clear_saved_data()
    elif choice == "4":
        troubleshoot_login_issues()
    else:
        open_youtube_with_login()
