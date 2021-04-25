# SHU-CourseHelper 

**Automatically select lessons, once available**

[中文版](README_zh_CN.md)

## **Introduction**

This program can refresh pages of SHU Course Selection System automatically and select courses once it is selection time or the courses are available.

If it is not selection time or the target courses are full, the program will update information automatically and try to select them if possible.


## **Quick Start**

This program can run on Windows, Linux and MacOS，Python installation is required.

Clone this project or download zip first.

Then open a terminal or shell and change directory to the project folder

### **Install Modules**

```bash
python -m pip install -r requirements.txt
```
### **Edit program config (optional)**

The program will ask you to input necessary information if config is incomplete

Use a text editor and open `courses.txt`

All the config items are explained in the table below

| Module    	| Variable         	| Comment                 |
|------------	|------------------	|------------------------|
| [Userinfo] 	| user             	| Username of your account |
| [Userinfo] 	| password         	| Your password 	       |
| [Userinfo] 	| encryptpassword  	| Encrypted password   	  |
| [Settings] 	| term             	| Term of course selection |
| [Settings] 	| querydelay       	| Delay of updating course information |
| [Settings] 	| checkselectdelay 	| Delay of checking selection time |
| [Settings] 	| warndiffcampus   	| Whether warn if you selected courses in a diffrent campus as you are in |
| [Courses]  	| course1          	| Course information: Course id,Teaher id  |
| [Courses]  	| course2          	| Same as above             |
|            	| ...              	|      	                  |

#### **Notice**
 - All configuration should be entered after the char "=" in a single line
 - It is recommended to only store encrypted password in case of leaking sensitive information
 - When `encryptpassword` is set，the program will neglect the value of `password`
 - Course information must be entered in the format of `Course id,Teaher id`. eg.：`00874008,1001`
 - The program will neglect invalid values in config
 - When a new term starts, you may need to change the value of `term`, or simply clear it

### **Run the Program**
```bash
python SCourseHelper.py
```
Once you entered/configured all the relevant information, the program will automatically start to function
在输入相关信息或者编辑配置后，程序将自动运行尝试选课/蹲课

### **Information Required**
1. `User:`
   
   Enter your username

2. `Password:`
   
   Enter your password

3. `Do you want to save encrypted credentials in config?[Y/N]`
   
   You can enter `Y` to save the credentials or enter `N` to reject.

4. `Select Term:`

   Select the term in the list above, enter its number

5. `Please enter the info of courses, enter nothing to finish`

   The program will prompt you for course information

   `Enter the course  id of course 1 :`

   Enter the 8-digit course id

   `Enter the teacher id of course 1 :`

   Enter the 4-digit teacher id

   You may enter 9 courses max at a single time
   
   Please make sure that all the information you input is correct, or the program will return an error



