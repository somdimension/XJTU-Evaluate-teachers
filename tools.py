import time
import re
import sys
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
# 删除原有的 driver 初始化代码
# q = Options()
# q.add_argument(r"user-data-dir=D:\coding\sb评教\rate.py")  # 禁用沙盒模式
# q.add_experimental_option('detach', True)  # 保持浏览器窗口打开
# driver = webdriver.Edge(service=Service("D:\coding\edgedriver_win64 (1)\msedgedriver.exe"), options=q)


# 修改函数定义，添加 driver 参数
def count_multiple_choice_questions(driver):
    try:
        # 使用更精确的XPath查找评教题目区域
        # 查找所有题目元素
        time.sleep(3)
        questions = driver.find_elements(By.XPATH, './/*[@id="txwj-index-card"]')
        question_texts = [question.text for question in questions]
        
        all_text = ''.join(question_texts)
        print(f"合并后的文本: {all_text}")
        
        # 修改正则表达式并添加匹配检查
        match = re.search(r'(\d+)、请写下老师教学方面', all_text)
        if match:
            print(f"题目数: {match.group(1)}")
            return int(match.group(1))
        else:
            print("警告: 无法通过正则匹配获取题目数，使用备用方法")
            
    except Exception as e:
        print(f"获取题目时出错: {e}")
        # 打印当前页面HTML用于调试
        print("当前页面HTML:", driver.page_source[:500])  
    return int(match.group(1))

def choose_verygood_and_praise_the_teacher(driver, question_num,Comments_text):
    # 初始XPath字符串，定位到评教页面中的第一个评分选项
    s = '//*[@id="txwj-index-card"]/div[1]/div/div[2]/div[2]/div/label[1]/input'
    # 存储所有生成的XPath的列表
    xpath_list = []
    for i in range(question_num):
        # 将字符串转为列表方便修改特定位置的数字
        s_list = list(s)
        # 修改XPath中label的索引位置（从1开始）
        s_list[31] = str(i+1)
        # 将列表转回字符串格式
        new_s = ''.join(s_list)
        # 将生成的XPath添加到列表中
        xpath_list.append(new_s)
        # 打印生成的XPath用于调试
        print(new_s)
    print("所有XPath已生成,请耐心等待。等了一分钟以上就别等了，寄了。")

    # 自动选择所有评分选项（全部选择第一个选项）
    
    # 选择方式，带有异常处理
    for xpath in xpath_list:
        try:
            element = WebDriverWait(driver, 0.1).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            element.click()
        except NoSuchElementException:
            print(f"未找到元素: {xpath}")
            continue
        except ElementClickInterceptedException:
            print(f"元素点击被拦截: {xpath}")
            continue
        except Exception as e:
            print(f"发生错误: {e}")
            continue
    print("所有评分选项已选择")
    driver.find_element(By.CLASS_NAME,'bh-txt-input__txtarea').send_keys(Comments_text)  # 填写评语内容
  
    # 填写评语内容
# question_num = count_multiple_choice_questions()
# count_multiple_choice_questions()
# choose_verygood_and_praise_the_teacher(question_num-1)
# time.sleep(1)

def get_element_xpath(driver, element):
    """
    递归生成元素的完整XPath路径
    参数:
        driver: WebDriver实例
        element: 要生成XPath的网页元素
    返回:
        该元素的完整XPath字符串
    """
    # 如果元素有id属性，直接使用id构建XPath（最简短的定位方式）
    if element.get_attribute("id"):
        return f'//*[@id="{element.get_attribute("id")}"]'
    
    # 如果是HTML根元素，返回基础路径
    if element == driver.find_element("tag name", "html"):
        return "/html"
    
    # 获取当前元素的父元素
    parent = element.find_element("xpath", "..")
    # 获取所有同级元素
    siblings = parent.find_elements("xpath", "*")
    # 获取当前元素的标签名（小写）
    tag_name = element.tag_name.lower()
    
    # 计算当前元素在同级相同标签中的位置索引
    index = 1
    for sibling in siblings:
        if sibling == element:  # 找到当前元素时停止计数
            break
        if sibling.tag_name.lower() == tag_name:  # 只统计相同标签名的元素
            index += 1
    
    # 递归获取父元素的XPath
    parent_xpath = get_element_xpath(driver, parent)
    # 组合成完整路径：父XPath + 当前标签名[索引]
    return f"{parent_xpath}/{tag_name}[{index}]"


def choose_element(driver, target_text):
    try:
        # 尝试查找包含目标文本的元素
        element = driver.find_element("xpath", f"//*[contains(text(), '{target_text}')]")
        xpath = get_element_xpath(driver, element)
        print(f"{xpath}")
        return xpath
    except NoSuchElementException:
        print(f"未找到包含文本'{target_text}'的元素")
        return False
    except Exception as e:
        print(f"查找元素时发生错误: {e}")
        return False

    # if xpath.endswith("div[4]/div[1]/span[2]"):
    #     name_of_teacher = xpath[:-len("div[4]/div[1]/span[2]")] + "div[2]/span"
    # else:
    #     name_of_teacher = xpath

    # print(name_of_teacher)
    #teacher_name_element = driver.find_element("xpath", name_of_teacher)
    # print(f"老师: {teacher_name_element.text}")
    
    # # 新增等待用户按Enter键的代码
    # input("按Enter键继续...")

def find_teacher_name(driver, xpath):
    # 查找老师姓名的XPath
    if xpath.endswith("div[4]/div[1]/span[2]"):
        name_of_teacher = xpath[:-len("div[4]/div[1]/span[2]")] + "div[2]/span"
    else:
        name_of_teacher = xpath

    print(name_of_teacher)
    teacher_name_element = driver.find_element("xpath", name_of_teacher)
    print(f"老师: {teacher_name_element.text}")
    print("按Enter键继续...")  # 删除控制台交互代码
    return teacher_name_element.text  # 确保返回姓名


def submit_result(driver):
    print("提交")
    driver.find_element(By.XPATH,'//*[@id="txwjFooter"]/a[1]').click()
    time.sleep(1)
    submit_button = choose_element(driver,'确认')
    driver.find_element(By.XPATH,submit_button).click()
    # 直接点击提交按钮

    # target_text = "提交"
    # element = driver.find_element("xpath", f"//*[contains(text(), '{target_text}')]")
    # print(element)
    # xpath = get_element_xpath(driver,element)
    # driver.find_element(By.XPATH,xpath).click()
    

# //*[@id="txwjFooter"]/a[1]
# //*[@id="dialogbeb7cb96-f01a-7ac7-c1e1-6f9f343584ab"]/div[1]/div[1]/div[2]/div[2]/a[1]
# //*[@id="txwjFooter"]/a[1]
# //*[@id="dialog524b6fe8-be2c-647c-918b-99b9ab4638fa"]/div[1]/div[1]/div[2]/div[2]/a[1]
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[3]/div[4]/div/span[2]
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[3]/div[2]/span

# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[8]/div[4]/div/span[2]
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[8]/div[2]/span

# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[20]/div[4]/div/span[2]
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[20]/div[2]/span
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[20]/div[2]/span
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[8]/div[2]/span
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div/div[8]/div[2]/span

# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div[1]/div[3]/div[2]/span
# //*[@id="jqxWidget71dfc9a0"]/div[2]/div[2]/div[2]/div[1]/div[3]/div[4]/div[1]/span[2]
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div[1]/div[16]/div[4]/div[1]/span[2]
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div[1]/div[13]/div[2]/span
# //*[@id="jqxWidgetd255ee49"]/div[2]/div[2]/div[2]/div[1]/div[15]/div[2]/span