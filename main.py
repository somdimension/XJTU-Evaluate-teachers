import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tools as rate
# 移除顶部的 import GUI as gui
# 仅在需要时局部导入


def evaluate_teaching(username, password, comment_text, gui_callback=None):
    """
    执行评教流程的封装函数

    :param username: 用户名
    :param password: 密码
    :param comment_text: 评语内容
    :return: (success, message) 元组，表示成功与否及对应信息
    """
    def get_driver_path():
        """获取msedgedriver路径"""
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
        driver_path = os.path.join(exe_dir, 'msedgedriver.exe')
        if not os.path.exists(driver_path):
            raise FileNotFoundError(
                "EdgeDriver未找到！请确保它与本程序在同一目录，并命名为'msedgedriver.exe'。\n"
                "请从以下地址下载正确版本：https://msedgewebdriverstorage.z22.web.core.windows.net/?form=MA13LH"
            )
        return driver_path  # 现在返回完整路径

    try:
        # 配置浏览器选项
        q = webdriver.EdgeOptions()
        # 通过driver_path获取目录
        driver_path = get_driver_path()
        exe_dir = os.path.dirname(driver_path)  # 正确获取目录路径
        q.add_argument(f'--user-data-dir={os.path.join(exe_dir, "temp_edge_profile")}')  # 添加唯一用户目录
        q.add_argument('--disable-infobars')  # 禁用信息栏
        q.add_argument('--no-first-run')  # 跳过首次运行向导
        
        service = Service(get_driver_path())
        driver = webdriver.Edge(service=service, options=q)  # 确保这里只初始化一次
        driver.maximize_window()
        driver.implicitly_wait(5)

        # 打开登录页
        print("正在访问目标网站...", flush=True)
        driver.get('https://ehall.xjtu.edu.cn/new/index.html')

        # 登录流程
        print("正在点击登录按钮...", flush=True)
        driver.find_element(By.CLASS_NAME, 'amp-no-login-zh').click()

        print("正在输入用户名...", flush=True)
        driver.find_element(By.NAME, 'username').send_keys(username)

        print("正在输入密码...", flush=True)
        driver.find_element(By.NAME, 'pwd').send_keys(password)

        print("正在提交登录...", flush=True)
        driver.find_element(By.ID, 'account_login').click()

        print("等待5秒确保页面加载...", flush=True)
        time.sleep(5)

        # 搜索评教服务
        print("正在点击顶部搜索框...", flush=True)
        driver.find_element(By.XPATH, '//*[@id="ampPageHeaderSearch"]/div[1]').click()

        print("等待2秒让搜索面板展开...", flush=True)
        time.sleep(2)

        print("正在点击评教...", flush=True)
        driver.find_element(By.XPATH,'//*[@id="ampServiceLabelNav"]/div[2]/ul/li[14]').click()
        driver.find_element(By.XPATH,'//*[@id="ampServiceCenterSearchApps"]/div/div/div/div[2]').click()

        print("等待1秒让页面加载...", flush=True)
        time.sleep(1)

        # 进入应用详情页
        try:
            print("尝试点击'进入'按钮...", flush=True)
            enter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ampDetailEnter"]'))
            )
            enter_button.click()
            print("成功点击'进入'按钮", flush=True)
        except Exception as e:
            print(f"点击'进入'按钮失败: {str(e)}", flush=True)
            print("当前页面URL:", driver.current_url, flush=True)
            print("尝试查找元素是否存在...", flush=True)

        # 切换窗口
        print("正在切换到新窗口...", flush=True)
        windows = driver.window_handles
        driver.switch_to.window(windows[1])

        # 进入学生评教界面
        print("正在点击'学生'标签...", flush=True)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, '学生'))
        ).click()

        print("正在点击评教入口...", flush=True)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="pjglTopCard"]/div/div[2]'))
        ).click()

        print("等待页面加载完成...", flush=True)
        time.sleep(1)

        # 开始评教流程
        print("正在点击评教列表...", flush=True)
        WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="tabName-content-1"]/div/div[1]'))
        ).click()

        time.sleep(2)

        while True:
            button_xpath = rate.choose_element(driver, '立即评教')
            if not button_xpath:
                break
            
            # 获取教师姓名
            teacher_name = rate.find_teacher_name(driver, button_xpath)
            
            # 调用GUI提示框并等待（通过回调接口）
            if gui_callback and teacher_name:
                gui_callback(teacher_name)  # 这里已经存在正确的回调传递
            
            driver.find_element(By.XPATH, button_xpath).click()
            
            question_num = rate.count_multiple_choice_questions(driver)
            rate.choose_verygood_and_praise_the_teacher(driver, question_num - 1, comment_text)
            rate.submit_result(driver)
            time.sleep(2)

        return True, "评教已完成"

    except Exception as e:
        return False, f"发生错误：{str(e)}"
    finally:
        try:
            driver.quit()
        except:
            pass