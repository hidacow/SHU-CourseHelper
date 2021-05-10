# SHU-CourseHelper 

**Automatically select lessons, once available**

[中文版](README_zh_CN.md)

## **Introduction**

This program can refresh pages of SHU Course Selection System automatically and select courses once it is selection time or the courses are available.

If it is not selection time or the target courses are full, the program will update information automatically and try to select them if possible.

[New]If the targeted course is conflicting with currently selected courses, you can **edit the config** and let the program return the courses automatically in order to select the targeted course.

## **Quick Start**

This program can run on Windows, Linux and MacOS，Python installation is required.

Clone this project or download zip first.

Then open a terminal or shell and change directory to the project folder

### **Install Modules**

```bash
python -m pip install -r requirements.txt
```
### **Edit program config (recommended)**

The program will ask you to input necessary information if config is incomplete

Use a text editor and open `courses.txt`

All the config items are explained in the table below

| Module    	| Variable         	| Comment                                                                 |
|------------	|------------------	|------------------------------------------------------------------------ |
| [Userinfo] 	| user             	| Username of your account                                                |
| [Userinfo] 	| password         	| Your password 	                                                        |
| [Userinfo] 	| encryptpassword  	| Encrypted password   	                                                  |
| [Settings] 	| term             	| Term of course selection                                                |
| [Settings] 	| querydelay       	| Delay of updating course information                                    |
| [Settings] 	| checkselectdelay 	| Delay of checking selection time                                        |
| [Settings] 	| warndiffcampus   	| Whether warn if you selected courses in a diffrent campus as you are in |
| [Courses]  	| course1          	| Course information: Course id,Teacher id or Course id,Teacher id,Replace Course id,Replace Teacher id|
| [Courses]  	| course2          	| Same as above                                                           |
|            	| ...              	|      	                                                                 |
#### **Editting Course config**
 - The program support two modes of parsing the config
   1. Normal mode: `Course id,Teacher id` 
   
      Example: `00874008,1001`
   
      The program will select course no.`00874008`, teacher no.`1001`

   2. Advanced mode：`课程号,教师号,待替换课程号,待替换教师号`

      Example: `00874008,1001,00874008,1002`
   
      Selected course no. `00874008`,teacher no.`1002`,
      
      but wish to replace it with course no.`00874008`, teacher no.`1001`
 - The courses to be selected must be valid in the system and not duplicated, or the program will run into error
 - In the second mode, when the target course can be selected, the program will automatically return the replace courese and select the target course. Meantime, the returned course will be selected again in case that the course was selected by others.
 - However, there is still possibility that both course are failed to select, use this feature at your own risk.
 - Course information items should be the form of `course`+number, you may add items like `course10=`,`course11=`... if needed.


#### **Notice**
 - All configuration should be entered after the char "=" in a single line
 - It is recommended to only store encrypted password in case of leaking sensitive information
 - When `encryptpassword` is set，the program will neglect the value of `password`
 - The program will neglect invalid values in config
 - When a new term starts, you may need to change the value of `term`, or simply clear it

### **Run the Program**
```bash
python SCourseHelper.py
```
Once you entered/configured all the relevant information, the program will automatically start to function

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
   
   Please make sure that all the information you input is correct, or the program will return an error

   The courses entered when prompted will be selected in the normal mode for the time being.


