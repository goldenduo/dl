"""
AI技术能力评测自动化脚本 - Mac版本（简化版）
功能：模拟用户登录网站并与AI助手进行技术问题问答交互，评估AI回答质量
"""
import time
import traceback
from typing import List, Dict, Any, Union, Optional

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI

# 配置参数
CONFIG = {
    "api_key": "sk-阿里百炼模型的apikey",  # OpenAI API密钥
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",  # API基础URL
    "model_name": "qwen-plus",  # 模型名称 限时免费
    "phone_number": "13802885134",  # 登录手机号
    "login_url": "https://cas.tools.cmic.site/cas/login?service=https%3A%2F%2Fportal.tools.cmic.site#/",  # 登录页面URL
    "chat_url": "https://portal.tools.cmic.site/#/aiChat",  # 聊天页面URL
    "timeout": 60,  # 等待元素超时时间(秒)
    "polling_interval": 3,  # 轮询间隔(秒)
    "local_chromedriver_path": r"/Users/duoduo/Downloads/chromedriver-mac-x64/chromedriver",
    "ai_resp_timeout": 300
}

# 初始对话消息
INITIAL_MESSAGES = [
    {
        "role": "system",
        "content": """你是一名资深devops和K8S技术专家"""
    },
    {
        "role": "user",
        "content": """请提供50个devops与K8S相关的技术问题，要求如下：
1、每个问题用|分隔；
2、不允许出现问题编号；
3、每个问题需满足：
   - 字数≤50字
   - 单行文本
   - 避免重复
   - 保持技术深度递进
4、严格禁止包含其他提示内容"""
    }
]

# XPath定义
XPATH = {
    "sim_auth": "//span[contains(text(),'SIM认证')]",
    "phone_input": "//input[@placeholder='请输入手机号码']",
    "login_button": "//button[@class='el-button el-button--primary login-btn']",
    "login_success": "//a[@href='#/portal/home']",
    "input_area": '//*[@placeholder="Enter发送，Shift+Enter换行，@触发快捷菜单"]',
    "send_button": '//div[@class="ai-footer-flex"]//img',
    "send_load": '//div[@class="ai-footer-flex"]/button[@class="aiSendLoad"]',
    "ai_answer": '//div[@id="ai-chat"]/div[@class="ai-chat-contant"]/div[last()]/div[@class="ai-user ai-answer"]//div[@class="ai-gpt"]',
    "ai_content": '//div[@class="ai-content"]',
    "ai_stop":  '//div[@class="ai-footer-flex"]/div[@class="ai-stop"]',
}


class AIEvaluator:
    """AI评测器类，用于自动化评测AI助手的技术能力"""

    def __init__(self, headless: bool = False):
        """
        初始化评测器

        参数:
            headless: 是否以无头模式运行浏览器
        """
        self.messages = INITIAL_MESSAGES.copy()
        self.client = self._init_openai_client()
        self.driver = None  # 延迟初始化

    def _init_openai_client(self) -> OpenAI:
        """初始化OpenAI客户端"""
        return OpenAI(
            api_key=CONFIG["api_key"],
            base_url=CONFIG["base_url"]
        )

    def _init_webdriver(self, headless: bool) -> webdriver.Chrome:
        """
        初始化Chrome浏览器驱动

        参数:
            headless: 是否以无头模式运行浏览器

        返回:
            webdriver.Chrome: 配置好的Chrome驱动
        """
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # Mac上推荐添加
        options.add_argument("--disable-dev-shm-usage")  # Mac上推荐添加
        if headless:
            options.add_argument("--headless")

        # 使用 Service 类指定 chromedriver 路径
        from selenium.webdriver.chrome.service import Service
        return webdriver.Chrome(
            service=Service(CONFIG["local_chromedriver_path"]),
            options=options
        )

    def wait_for_element(self, xpath: str, timeout: int = None,
                        multiple: bool = False, get_text: bool = False) -> Union[
                            webdriver.remote.webelement.WebElement,
                            str,
                            List[webdriver.remote.webelement.WebElement],
                            List[str]
                        ]:
        """
        等待元素出现并返回元素或元素文本

        参数:
            xpath: 元素的XPath
            timeout: 超时时间(秒)，默认使用CONFIG中的timeout
            multiple: 是否返回多个元素
            get_text: 是否返回元素文本

        返回:
            根据参数返回元素、元素文本或它们的列表

        异常:
            TimeoutException: 超时未找到元素
        """
        if timeout is None:
            timeout = CONFIG["timeout"]

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if multiple:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        return [e.text for e in elements] if get_text else elements
                else:
                    element = self.driver.find_element(By.XPATH, xpath)
                    return element.text if get_text else element
            except (NoSuchElementException, StaleElementReferenceException):
                time.sleep(CONFIG["polling_interval"])

        raise TimeoutException(f"等待元素超时: {xpath}")

    def get_ai_response(self) -> str:
        """
        获取OpenAI模型的回答

        返回:
            str: 模型的回答内容
        """
        completion = self.client.chat.completions.create(
            model=CONFIG["model_name"],
            messages=self.messages
        )
        return completion.choices[0].message.content

    def get_ai_answer(self, xpath: str) -> str:
        """
        获取AI助手的回答，确保回答已完全生成

        参数:
            xpath: AI回答元素的XPath

        返回:
            str: AI助手的完整回答
        """
        # 等待ai-stop元素消失（表示回答结束）
        try:
            WebDriverWait(self.driver, CONFIG["ai_resp_timeout"]).until(
                EC.invisibility_of_element_located((By.XPATH, XPATH["ai_stop"]))
            )
        except TimeoutException:
            print("⚠ 等待加载结束超时")
            # 超时后继续执行，可能返回不完整回答

        # 获取最终回答内容
        ai_elements = self.wait_for_element(xpath, multiple=True)
        current_text = ''.join([element.text.strip() for element in ai_elements])
        print(f"回答已生成完毕 ({len(current_text)} 字符)")
        return current_text

    def login(self) -> None:
        """
        登录到指定网站

        异常:
            Exception: 登录过程中的任何错误
        """
        try:
            print("正在访问登录页面...")
            self.driver.get(CONFIG["login_url"])

            # 点击SIM认证
            print("正在进行SIM认证登录...")
            sim_auth = WebDriverWait(self.driver, CONFIG["timeout"]).until(
                EC.element_to_be_clickable((By.XPATH, XPATH["sim_auth"]))
            )
            sim_auth.click()

            # 输入手机号
            inputs = self.driver.find_elements(By.XPATH, XPATH["phone_input"])
            for input_field in inputs:
                input_field.send_keys(CONFIG["phone_number"])

            # 点击登录按钮
            login_button = self.driver.find_element(By.XPATH, XPATH["login_button"])
            login_button.click()

            # 等待登录成功
            WebDriverWait(self.driver, CONFIG["timeout"]).until(
                EC.presence_of_element_located((By.XPATH, XPATH["login_success"]))
            )
            print("✓ 登录成功")

            # 打开AI聊天页面
            self.driver.get(CONFIG["chat_url"])
            print("✓ 已打开AI聊天页面")

            # 移除可能妨碍操作的元素
            try:
                self.driver.execute_script(
                    "const element = document.getElementById('KunlunDrawer'); "
                    "if(element) element.remove();"
                )
            except Exception:
                pass  # 忽略如果元素不存在

        except Exception as e:
            print(f"❌ 登录失败: {e}")
            raise

    def check_already_logged_in(self) -> bool:
        """检查是否已处于登录状态"""
        try:
            self.driver.get(CONFIG["chat_url"])
            # 检查关键元素是否存在
            self.wait_for_element(XPATH["input_area"], timeout=10)
            self.wait_for_element(XPATH["ai_answer"], timeout=10)
            print("✓ 检测到有效登录状态")
            return True
        except TimeoutException:
            print("⚠ 未检测到登录状态，需要重新登录")
            return False

    def run_evaluation(self) -> None:
        """运行AI技术能力评测流程"""
        try:
            print("提示：按 Ctrl+C 可随时退出程序")

            retry_count = 0
            max_retries = 3

            # 生成全部50个问题，最多重试3次
            while retry_count < max_retries:
                print(f"\n正在生成全部技术问题... (尝试次数: {retry_count+1}/{max_retries})")
                ai_response = self.get_ai_response()
                print(f"AI 生成的技术问题：{ai_response}")
                all_questions = ai_response.split('|')

                # 新增：当问题数为1时尝试换行切割
                if len(all_questions) == 1 and all_questions[0].strip() != "":
                    print("⚠ 检测到单个问题，尝试通过换行符二次切割")
                    all_questions = [q.strip() for q in all_questions[0].split('\n') if q.strip()]
                    print(f"✓ 通过换行符切割获得{len(all_questions)}个问题")

                # 过滤无效问题
                valid_questions = []
                for i, question in enumerate(all_questions):
                    if not question:
                        print(f"⚠ 第{i + 1}个问题为空，已跳过")
                        continue
                    if len(question) > 50:
                        print(f"⚠ 第{i + 1}个问题超长（{len(question)}字），已截取前50字")
                        question = question[:50]  # 截取前50字

                    valid_questions.append(question.strip())
                    print(f"Q{i + 1}: {question[:50]}" + ("..." if len(question) > 50 else ""))

                # 更新问题列表
                all_questions = valid_questions

                # 验证问题数量并处理
                if len(all_questions) >= 10:
                    if len(all_questions) > 50:
                        print(f"⚠ 检测到多余问题，自动截取前50个（当前{len(all_questions)}个）")
                        all_questions = all_questions[:50]
                    print(f"✓ 成功生成{len(all_questions)}个技术问题")
                    break  # 成功生成足够数量的问题
                else:
                    retry_count += 1
                    print(f"❌ 问题数量不足（{len(all_questions)}个），正在进行第{retry_count}次重试...")
                    time.sleep(2)  # 等待2秒后重试

            if retry_count >= max_retries:
                raise ValueError(f"生成问题失败，经过{max_retries}次重试仍未达到最低问题数量要求")

            # 延迟初始化浏览器驱动（在问题生成后）
            print("\n正在初始化浏览器驱动...")
            self.driver = self._init_webdriver(False)

            # 快速检测登录状态
            if not self.check_already_logged_in():
                # 执行完整登录流程
                self.login()

            # 记录问题开始索引
            question_index = 0

            # 逐个处理问题
            for question in all_questions:
                question = question.strip()
                if not question:
                    continue

                print(f"\n--- 第 {question_index+1} 题 ---")
                print(f"问题: {question}")

                # 输入问题
                input_area = self.wait_for_element(XPATH["input_area"])
                input_area.send_keys(question)

                # 点击发送按钮
                send_button = WebDriverWait(self.driver, 1000).until(
                    EC.element_to_be_clickable((By.XPATH, XPATH["send_button"]))
                )
                send_button.click()
                print(f"✓ 已发送问题")

                time.sleep(3 * CONFIG["polling_interval"])

                # 获取AI回答
                print("等待AI回答...")
                ai_answer = self.get_ai_answer(XPATH["ai_answer"])
                print(f"AI回答: {ai_answer[:100]}{'...' if len(ai_answer) > 100 else ''}")

                # 新增AI生成失败处理
                if "生成失败，请重新生成" in ai_answer:
                    print("⚠ 检测到生成失败，尝试点击停止按钮...")
                    try:
                        # 检查停止按钮是否存在
                        stop_button = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, XPATH["ai_stop"]))
                        )
                        if stop_button:
                            stop_button.click()
                            print("✓ 已点击停止按钮")
                            time.sleep(CONFIG["polling_interval"])  # 等待界面刷新
                            continue  # 跳过当前循环，重新生成问题
                    except TimeoutException:
                        print("⚠ 未找到停止按钮，继续执行")

                # 更新对话历史
                self.messages.append({"role": "user", "content": ai_answer})

                # 记录问题索引
                question_index += 1

        except KeyboardInterrupt:
            print("\n检测到 Ctrl+C，正在退出...")
        except Exception as e:
            print(f"\n❌ 评测过程中发生错误:")
            traceback.print_exc()
        finally:
            if self.driver:
                print("\n正在关闭浏览器...")
                self.driver.quit()
                print("✓ 已关闭浏览器")

            print("程序已退出")


if __name__ == '__main__':
    evaluator = AIEvaluator(headless=False)
    evaluator.run_evaluation()