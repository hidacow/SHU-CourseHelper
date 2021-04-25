# SHU抢课助手 自动选课/抢课/捡漏

[English Version](README.md)

## **功能简介**

本项目可以实现在SHU选课系统中自动刷新页面，若在选课时间且目标课程有空余会自动选课。

若未到选课或目标课程暂无空余，程序能够定时刷新信息，一旦选课开始/有人退课（课程容量空余）将会自动尝试选课

## **快速开始**

本项目适用于Windows，Linux与MacOS，需要安装Python环境

首先先将本项目clone到本地/下载压缩包并解压

然后打开一个命令提示符/shell并切换路径到该文件夹

### **安装依赖**

```bash
python -m pip install -r requirements.txt
```
### **编辑配置（可选）**

若不进行任何配置或缺失部分配置，在运行程序时会提示您输入相关必要信息

使用文本编辑器打开目录中的`courses.txt`，所有的参数作用见下表

| 模块       	| 变量             	| 说明 	                  |
|------------	|------------------	|------------------------|
| [Userinfo] 	| user             	| 用户名                   |
| [Userinfo] 	| password         	| 密码 	                   |
| [Userinfo] 	| encryptpassword  	| 加密的密码           	  |
| [Settings] 	| term             	| 选课学期 	              |
| [Settings] 	| querydelay       	| 更新课程信息延时	       |
| [Settings] 	| checkselectdelay 	| 查询选课开始延时 	       |
| [Settings] 	| warndiffcampus   	| 是否提示选课跨校区       |
| [Courses]  	| course1          	| 课程信息：课程号,教师号  |
| [Courses]  	| course2          	| 同上                    |
|            	| ...              	|      	                  |

#### **说明**
 - 所有配置都在"="后填写，不能换行
 - 建议仅储存加密的密码以防泄露明文密码
 - 若`encryptpassword`不为空时，程序会忽略`password`的值
 - 课程信息必须按照`课程号,教师号`的格式填写，示例：`00874008,1001`
 - 程序会忽略格式不正确的配置
 - 在进行新学期选课时，可能需要更改`term`的值，或将其清空

### **运行程序**
```bash
python SCourseHelper.py
```
在输入相关信息或者编辑配置后，程序将自动运行尝试选课/蹲课

### **程序运行时可能需要您提供的信息**
1. `User:`
   
   请输入您的用户名

2. `Password:`
   
   请输入您的密码

3. `Do you want to save encrypted credentials in config?[Y/N]`
   
   你可以输入`Y`将用户名与加密后的密码保存在配置文件中，输入`N`以拒绝

4. `Select Term:`

   在上面的列表中选择您要选课的学期，输入它的编号

5. `Please enter the info of courses, enter nothing to finish`

   程序将会提示您输入您想选课程的相关信息

   `Enter the course  id of course 1 :`

   输入8位课程号

   `Enter the teacher id of course 1 :`

   输入4位教师号

   若想终止输入，请在程序提示输入下一个课程信息时什么都不要输入，直接按回车

   你可以一次性最多输入9门课程的相关信息

   请确保你输入的课程信息都是正确的，否则程序将在接下来的运行过程中报错



