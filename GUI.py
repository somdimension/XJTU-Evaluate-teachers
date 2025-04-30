import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk, scrolledtext, messagebox
import sys
import threading
from main import evaluate_teaching

class LoginApp:
    def __init__(self, master):
        """初始化评教系统界面"""
        self.master = master
        master.title("评教系统 - 专业版")
        master.geometry("800x600")
        master.minsize(600, 400)
        
        # 设置窗口居中
        self.center_window()
        
        # 配置主题样式
        self.configure_styles()
        
        # 创建主框架
        main_frame = ttk.Frame(master, padding="20")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # 配置网格权重
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)  # 输出区域行权重

        # 用户名输入区域
        ttk.Label(main_frame, text="用户名:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.username_entry = ttk.Entry(main_frame, width=40)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
       # 密码输入区域
 
        ttk.Label(main_frame, text="密码:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        # 密码输入框和显示按钮
        password_frame = ttk.Frame(main_frame)
        password_frame.grid(row=1, column=1, sticky='n')
        self.password_entry = ttk.Entry(password_frame, width=46, show="*")  
        self.password_entry.pack(side='left', fill='x', expand=True)
        self.show_password_btn = ttk.Button(password_frame, text="👁", width=3,
                                          command=self.toggle_password)
        self.show_password_btn.pack(side='left', padx=2)

        # 评语输入区域
        ttk.Label(main_frame, text="评语内容:").grid(row=2, column=0, padx=5, pady=5, sticky='nw')
        self.comment_entry = tk.Text(main_frame, height=5, width=40, 
                                    font=('微软雅黑', 10), wrap='word',
                                    borderwidth=2, relief='sunken')
        self.comment_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.comment_entry.insert('1.0', "Ciallo～(∠・ω< )⌒☆【默认评语，请修改】")
        # self.comment_entry.bind('<FocusIn>', self.clear_default_text)

        # 登录按钮
        self.login_button = ttk.Button(main_frame, text="开始评教", 
                                     style='Accent.TButton',
                                     command=self.start_evaluation)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=15, sticky='ew')

        # 输出区域
        self.output_area = scrolledtext.ScrolledText(main_frame, height=20, width=60,
                                                    font=('Consolas', 9),
                                                    wrap='word')
        self.output_area.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        # 配置输出区域标签样式
        self.output_area.tag_configure('info', foreground='blue')
        self.output_area.tag_configure('error', foreground='red')
        self.output_area.tag_configure('success', foreground='green')

        # 初始化重定向
        sys.stdout = TextRedirector(self.output_area, "stdout")
        
        # 初始化事件对象
        self.continue_event = threading.Event()
        self.waiting_for_input = False
        
        # 绑定自定义事件
        master.bind('<<ShowContinueDialog>>', self.show_continue_with_name)
    def configure_styles(self):
        """配置界面样式主题"""
        style = ttk.Style()
        style.theme_use('clam')  # 改为Windows Vista风格主题

        # 配置按钮样式
        style.configure('Accent.TButton', 
                      padding=6,
                      relief='flat',
                      background='#1E90FF',
                      foreground='white')
        style.map('Accent.TButton',
                 background=[('active', '#4169E1')])
        
        # 配置输入框样式
        style.configure('TEntry', padding=5, relief='flat', borderwidth=1)
        
        # 配置框架背景
        style.configure('TFrame', background='#F5F5F5')

    def center_window(self):
        """将窗口居中显示"""
        self.master.update_idletasks()  # 添加self引用
        width = self.master.winfo_width()  # 修正变量名
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'+{x}+{y}')  # 保持原窗口尺寸不变

    def toggle_password(self):
        """切换密码可见性"""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
            self.show_password_btn.config(text="👁‍🗨")
        else:
            self.password_entry.config(show='*')
            self.show_password_btn.config(text="👁")
    
    
    
    def show_continue_with_name(self, event=None):
        """带教师姓名的对话框"""
        top = tk.Toplevel(self.master)
        top.title("确认评教")
        top.attributes('-topmost', True)  # 添加这行设置窗口置顶
        tk.Label(top, text=f"即将评教：{self.current_teacher}").pack(pady=10)
        tk.Button(top, text="继续", command=lambda: self.on_continue(top)).pack(pady=5)
        top.grab_set()
    
    def on_continue(self, top):
        """继续按钮处理"""
        top.destroy()
        self.continue_event.set()

    def start_evaluation(self):
        """开始评教按钮点击事件处理"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        comment_text = self.comment_entry.get('1.0', 'end-1c')  # 获取Text组件内容
        
        if not username or not password:
            print("请输入用户名和密码！")
            return
            
        print("正在启动评教程序...")
        
        # 禁用按钮防止重复点击
        self.login_button.config(state=tk.DISABLED)
        
        #在新线程中运行main.py避免界面卡顿
        thread = threading.Thread(
            target=self.run_main_script,
            args=(username, password, comment_text, self.show_teacher_dialog),  # 传递4个参数
            daemon=True  # 设为守护线程
        )
        thread.start()

    def show_teacher_dialog(self, name):
        """显示教师姓名的对话框"""
        self.current_teacher = name
        # 使用主线程队列执行GUI操作
        self.master.after(0, lambda: 
            self.master.event_generate('<<ShowContinueDialog>>'))
        self.continue_event.wait()
        self.continue_event.clear()

    def run_main_script(self, username, password, comment_text, gui_callback):  # 添加回调参数
        """执行评教主脚本"""
        try:
            # 直接调用函数（移除所有子进程相关代码）
            success, message = evaluate_teaching(username, password, comment_text, gui_callback)  # 添加第四个参数
            print(message)
            
        except Exception as e:
            error_msg = f"运行出错: {str(e)}"
            print(error_msg)
        finally:
            # 恢复按钮状态
            self.master.after(0, lambda: self.login_button.config(state=tk.NORMAL))
            self.waiting_for_input = False

class TextRedirector:
    """重定向标准输出到GUI文本框的类"""
    def __init__(self, widget, tag="stdout"):
        self.widget = widget  # 目标文本框组件
        self.tag = tag  # 文本标签
    
    def write(self, text):
        """写入文本到GUI组件"""
        self.widget.insert(tk.END, text, (self.tag,))
        self.widget.see(tk.END)  # 自动滚动到底部
    
    def flush(self):
        """空实现，满足文件接口要求"""
        pass

if __name__ == "__main__":
    """程序入口"""
    root = tk.Tk()
    root.attributes('-topmost', True)  # 添加这行使窗口保持最前
    app = LoginApp(root)
    root.mainloop()  # 启动主事件循环