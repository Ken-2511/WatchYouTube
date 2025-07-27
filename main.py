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
import random

# 配置常量
COOKIE_FILE = "youtube_cookies.json"
DEFAULT_VIDEO_URL = "https://youtu.be/_wqlHmhCqug?si=IhySzXenMXA2IR_0"
CHANNEL_URL = "https://www.youtube.com/@AltonFrederickpreaching/videos"

def save_cookies(driver):
    """保存当前浏览器的cookies到文件"""
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
    """从文件加载cookies到浏览器"""
    try:
        if not os.path.exists(COOKIE_FILE):
            print("📝 未找到已保存的cookies文件")
            return False
        
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        driver.get("https://www.youtube.com")
        time.sleep(2)
        
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
    """检查是否已登录YouTube"""
    try:
        driver.get("https://www.youtube.com")
        wait = WebDriverWait(driver, 10)
        
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#avatar-btn")))
            print("✅ 检测到已登录状态")
            return True
        except:
            try:
                driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Sign in')]")
                print("❌ 未登录状态")
                return False
            except:
                print("⚠️ 无法确定登录状态")
                return False
    except Exception as e:
        print(f"❌ 检查登录状态失败: {e}")
        return False

def get_channel_videos(driver, channel_url):
    """获取频道页面的视频列表"""
    try:
        print(f"🔍 正在访问频道主页: {channel_url}")
        driver.get(channel_url)
        time.sleep(5)
        
        # 滚动页面加载更多视频
        print("📜 正在滚动页面加载视频...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
        
        # 获取所有视频容器
        video_containers = driver.find_elements(By.CSS_SELECTOR, "#contents ytd-rich-item-renderer")
        
        if not video_containers:
            print("❌ 未找到任何视频")
            return []
        
        video_info_list = []
        for container in video_containers:
            try:
                # 获取缩略图元素
                thumbnail = container.find_element(By.CSS_SELECTOR, "#thumbnail img")
                # 获取视频链接
                video_link = container.find_element(By.CSS_SELECTOR, "a#thumbnail")
                
                video_info = {
                    'thumbnail': thumbnail,
                    'link': video_link,
                }
                video_info_list.append(video_info)
                
            except Exception as e:
                continue
        
        print(f"✅ 找到 {len(video_info_list)} 个视频")
        return video_info_list
        
    except Exception as e:
        print(f"❌ 获取频道视频失败: {e}")
        return []

def skip_ad_if_present(driver):
    """检查并跳过广告"""
    try:
        time.sleep(3)
        skip_button = driver.find_element(By.CSS_SELECTOR, ".ytp-skip-ad-button")
        if skip_button.is_displayed() and skip_button.is_enabled():
            print("📺 发现广告，正在跳过...")
            skip_button.click()
            time.sleep(2)
            print("✅ 广告已跳过")
            return True
    except:
        pass
    return False

def navigate_back_to_channel(driver, channel_url):
    """导航回到频道页面"""
    try:
        print("🔙 正在返回频道页面...")
        driver.back()
        time.sleep(3)
        
        current_url = driver.current_url
        if "@AltonFrederickpreaching" in current_url and "videos" in current_url:
            print("✅ 已返回频道页面")
            return True
        
        # 再试一次后退
        driver.back()
        time.sleep(3)
        
        current_url = driver.current_url
        if "@AltonFrederickpreaching" in current_url and "videos" in current_url:
            print("✅ 已返回频道页面")
            return True
        
        # 直接导航到频道页面
        driver.get(channel_url)
        time.sleep(3)
        print("✅ 已返回频道页面")
        return True
        
    except Exception as e:
        print(f"❌ 返回频道页面失败: {e}")
        return False

def wait_for_video_duration(driver, video_url, max_wait_time=None):
    """等待视频播放完成，通过监控URL变化来判断"""
    try:
        print(f"🎬 开始监控视频播放: {video_url}")
        start_time = time.time()
        
        while True:
            time.sleep(1)  # 每隔1秒检查一次
            current_url = driver.current_url
            elapsed_time = int(time.time() - start_time)
            
            # 检查当前URL是否还包含原视频的标识
            if video_url not in current_url:
                print(f"✅ 视频播放完成！播放时长: {elapsed_time}秒")
                return True
            
            # 打印进度（每10秒打印一次）
            if elapsed_time % 10 == 0 and elapsed_time > 0:
                print(f"⏱️ 视频播放中... 已播放 {elapsed_time} 秒")
            
            # 如果设置了最大等待时间
            if max_wait_time and elapsed_time >= max_wait_time:
                print(f"⏰ 达到最大等待时间 {max_wait_time} 秒，停止监控")
                return False
                
    except KeyboardInterrupt:
        print("\n⚠️ 用户手动中断视频监控")
        return False
    except Exception as e:
        print(f"❌ 监控视频播放时发生错误: {e}")
        return False

def select_random_video_with_duration(driver, video_info_list, channel_url):
    """随机选择一个视频并点击播放，支持时长处理和自动回退"""
    try:
        if not video_info_list:
            print("❌ 没有可选择的视频")
            return False
        
        selected_video_info = random.choice(video_info_list)
        selected_video = selected_video_info['thumbnail']
        video_link = selected_video_info['link']
        
        print(f"🎲 随机选择视频 (共{len(video_info_list)}个视频可选)")
        
        # 滚动到选中的视频位置
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", selected_video)
        time.sleep(2)
        
        try:
            print("🖱️ 正在点击选中的视频...")
            
            # 获取视频链接地址
            video_url = video_link.get_attribute('href')
            print(f"🔗 视频链接: {video_url}")
            
            video_link.click()
            time.sleep(5)
            
            # 检查并跳过广告
            skip_ad_if_present(driver)
            
            # 尝试点击播放按钮
            try:
                play_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-large-play-button"))
                )
                play_button.click()
                print("▶️ 已自动点击播放按钮")
            except:
                print("ℹ️ 视频已自动播放或无需手动点击")
            
            # 再次检查广告
            time.sleep(3)
            skip_ad_if_present(driver)
            
            print("✅ 视频播放成功！")
            
            # 等待视频播放完成
            print("🕒 开始监控视频播放状态...")
            if wait_for_video_duration(driver, video_url):
                return navigate_back_to_channel(driver, channel_url)
            else:
                print("⚠️ 视频监控结束")
                return True
            
        except Exception as click_error:
            print(f"❌ 点击视频失败: {click_error}")
            try:
                print("🔄 尝试备用点击方案...")
                
                # 获取视频链接地址（备用方案）
                video_url = video_link.get_attribute('href')
                
                selected_video.click()
                time.sleep(5)
                skip_ad_if_present(driver)
                
                print("🕒 开始监控视频播放状态...")
                if wait_for_video_duration(driver, video_url):
                    navigate_back_to_channel(driver, channel_url)
                
                return True
            except:
                print("❌ 备用点击方案也失败")
                return False
        
    except Exception as e:
        print(f"❌ 选择视频失败: {e}")
        return False

def setup_chrome_options():
    """设置Chrome选项"""
    chrome_options = Options()
    
    # 基本设置
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--window-position=0,0")
    
    # 反检测设置
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 增强反检测措施
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-permissions-api")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    
    # 日志抑制
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-gpu-logging")
    chrome_options.add_argument("--disable-ml-model-service")
    chrome_options.add_argument("--disable-component-update")
    
    # 设置用户数据目录
    user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # 设置环境变量
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    
    # 随机用户代理
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    # 浏览器首选项
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "plugins": 1,
            "popups": 0,
            "geolocation": 2,
            "media_stream": 2,
        },
        "profile.default_content_settings": {"popups": 0},
        "profile.managed_default_content_settings": {"images": 1}
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options

def create_driver():
    """创建Chrome WebDriver实例"""
    chrome_options = setup_chrome_options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 执行反检测脚本
    stealth_js = """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    try {
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        Object.defineProperty(screen, 'colorDepth', {get: () => 24});
        Object.defineProperty(screen, 'pixelDepth', {get: () => 24});
        Object.defineProperty(navigator, 'permissions', {get: () => undefined});
        if (!window.chrome || !window.chrome.runtime) {
            Object.defineProperty(window, 'chrome', {
                value: {runtime: {}},
                writable: false,
                enumerable: true,
                configurable: false
            });
        }
    } catch(e) {}
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """
    driver.execute_script(stealth_js)
    driver.set_window_size(1920, 1080)
    
    return driver

def handle_login_flow(driver):
    """处理登录流程"""
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

def youtube_login(driver):
    """引导用户登录YouTube"""
    print("\n🔐 开始YouTube登录流程...")
    print("📺 正在打开YouTube，请按以下步骤登录:")
    print("1. 等待页面加载完成")
    print("2. 点击右上角的'登录'按钮")
    print("3. 在弹出的窗口中输入您的Google账号和密码")
    print("4. 完成任何二步验证（如果需要）")
    print("5. 确认登录成功后，回到此程序")
    
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
        return False

def open_channel_and_play_random_video():
    """打开指定频道并随机播放一个视频"""
    try:
        print("🚀 正在启动Chrome浏览器...")
        driver = create_driver()
        print("✅ Chrome浏览器已启动完成！")
        print("=" * 50)
        
        # 处理登录流程
        logged_in = handle_login_flow(driver)
        
        print(f"\n🎬 正在访问频道主页...")
        print(f"🔗 频道: {CHANNEL_URL}")
        
        # 获取频道视频列表
        video_info_list = get_channel_videos(driver, CHANNEL_URL)
        
        if video_info_list:
            while True:
                success = select_random_video_with_duration(driver, video_info_list, CHANNEL_URL)
            
            if success:
                print("\n" + "=" * 50)
                print("✅ 随机视频已成功打开！")
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
                
                input()
            else:
                print("❌ 无法播放随机视频")
                input("按Enter键关闭浏览器...")
        else:
            print("❌ 未能获取到频道视频列表")
            input("按Enter键关闭浏览器...")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查网络连接是否正常")
        print("2. 确保Chrome浏览器已正确安装")
        print("3. 关闭其他Chrome窗口后重试")
        print("4. 重启程序或重启计算机")
        input("按Enter键退出...")
        
    finally:
        if 'driver' in locals():
            try:
                if check_login_status(driver):
                    save_cookies(driver)
                    print("💾 登录状态已保存")
            except:
                pass
            driver.quit()
            print("🔒 浏览器已关闭")

def open_default_video():
    """使用浏览器打开默认视频"""
    try:
        print("🚀 正在启动Chrome浏览器...")
        driver = create_driver()
        print("✅ Chrome浏览器已启动完成！")
        print("=" * 50)
        
        # 处理登录流程
        logged_in = handle_login_flow(driver)
        
        print(f"\n🎥 正在打开YouTube视频...")
        print(f"🔗 链接: {DEFAULT_VIDEO_URL}")
        print("⏳ 请稍等，正在加载视频页面...")

        driver.get(DEFAULT_VIDEO_URL)
        
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
        
        print("\n💡 视频播放监控:")
        print("- 程序将自动监控视频播放状态")
        print("- 视频播放完毕后会自动关闭浏览器")
        print("- 您也可以手动按Ctrl+C强制退出")
        print("=" * 50)
        print("🔍 正在监控视频播放状态...")
        
        # 持续监控当前URL
        original_url = DEFAULT_VIDEO_URL
        try:
            while True:
                time.sleep(5)
                current_url = driver.current_url
                
                if original_url not in current_url:
                    print(f"\n🎬 检测到页面跳转: {current_url}")
                    print("✅ 视频播放完毕，正在自动关闭浏览器...")
                    break
        except KeyboardInterrupt:
            print("\n⚠️ 用户手动中断，正在关闭浏览器...")
        except Exception as e:
            print(f"\n❌ 监控过程中发生错误: {e}")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查网络连接是否正常")
        print("2. 确保Chrome浏览器已正确安装")
        print("3. 关闭其他Chrome窗口后重试")
        print("4. 重启程序或重启计算机")
        input("按Enter键退出...")
        
    finally:
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
    """清除保存的cookies和用户数据"""
    try:
        if os.path.exists(COOKIE_FILE):
            os.remove(COOKIE_FILE)
            print("✅ 已清除保存的cookies")
        
        user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        if os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir)
            print("✅ 已清除Chrome用户数据")
        
        print("🔄 所有保存的数据已清除")
    except Exception as e:
        print(f"❌ 清除数据时发生错误: {e}")

def open_youtube_alternative():
    """替代方案：使用默认浏览器打开YouTube"""
    print(f"🌐 使用默认浏览器打开YouTube视频: {DEFAULT_VIDEO_URL}")
    webbrowser.open(DEFAULT_VIDEO_URL)
    print("✅ 视频已在默认浏览器中打开")

def troubleshoot_login_issues():
    """登录问题故障排除指南"""
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
    print("🎬 YouTube视频播放器 v2.3 - 简化版")
    print("=" * 50)
    print("选择功能:")
    print("1. 📺 访问指定频道并随机播放视频")
    print("2. 🎥 播放默认视频 (带监控)")
    print("3. 🌐 使用默认浏览器（简单快速）")
    print("4. 🗑️ 清除保存的登录数据")
    print("5. 🛠️ 登录问题故障排除指南")
    print("=" * 50)
    
    choice = input("请输入选择 (1-5): ").strip()
    
    if choice == "1":
        open_channel_and_play_random_video()
    elif choice == "2":
        open_default_video()
    elif choice == "3":
        open_youtube_alternative()
    elif choice == "4":
        clear_saved_data()
    elif choice == "5":
        troubleshoot_login_issues()
    else:
        print("❌ 无效选择，请输入 1-5 之间的数字")
        input("按Enter键退出...")
