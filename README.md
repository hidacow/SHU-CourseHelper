# SHU-CourseHelper

**Automatically select lessons, once available**

[中文版](README_zh_CN.md)

## **Introduction**

This program can refresh pages of SHU Course Selection System automatically and select courses once it is selection time or the courses are available.

If it is not selection time or the target courses are full, the program will update information automatically and try to select them if possible.

If the targeted course is conflicting with currently selected courses, you can let the program return the courses automatically in order to select the targeted course.

## **Version History**

**Ver 1.3.2 (2023.2.13)**

- Support comments in config file. You can use `#`  to comment, comments starting with `;` will disappear after running the program
- Fix: Chinese comments in config file cannot be parsed
- Judge new situation: `Already selected the course and passed in previous terms`

**Ver 1.3.1 (2022.2.19)**

This update involves new dependency: [tenacity](https://github.com/jd/tenacity), please install it before running the script

- Requests will now retry if failed

- Minor improvements

  > Notice: Due to changes in course selection system rules, protection feature in Advanced mode no longer works

**Ver 1.3 (2022.1.8)**

- Various fixes in program logic
- User-friendly prompts of common errors
- Add logging and related settings (need to update config file)

**Ver 1.2.1 (2022.1.4)**

- Fix parsing course queries

## **Quick Start**

This program can run on Windows, Linux and MacOS, Python3 installation is required.

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

| Module     | Variable         | Comment                                                      |
| ---------- | ---------------- | ------------------------------------------------------------ |
| [Userinfo] | user             | Username of your account                                     |
| [Userinfo] | password         | Your password                                                |
| [Userinfo] | encryptpassword  | Encrypted password                                           |
| [Settings] | term             | Term of course selection                                     |
| [Settings] | querydelay       | Delay of updating course information (sec)                   |
| [Settings] | checkselectdelay | Delay of checking selection time (sec)                       |
| [Settings] | warndiffcampus   | Whether warn if you selected courses in a diffrent campus as you are in (non-zero:True, 0:False) |
| [Settings] | autoclearscreen  | Whether clear screen after every retry (non-zero:True, 0:False) |
| [Settings] | keeplogs         | Whether keep logs(non-zero:True, 0:False)                    |
| [Settings] | loglevel         | Integer. Log level below this value will be ignored.         |
| [Courses]  | course1          | Course information: Course id,Teacher id or Course id,Teacher id,Replace Course id,Replace Teacher id |
| [Courses]  | course2          | Same as above                                                |
|            | ...              |                                                              |

Log levels are explained in the table below.

| Level      | Value |
| ---------- | ----- |
| `CRITICAL` | 5     |
| `ERROR`    | 4     |
| `WARNING`  | 3     |
| `INFO`     | 2     |
| `DEBUG`    | 1     |

The default log level is `INFO`, which is also the recommended level if you enable logging

#### **Editing Course config**

- The program support two modes of parsing the config

  1. Normal mode: `Course id,Teacher id`

      Example: `00874008,1001`

      The program will select course no.`00874008`, teacher no.`1001`

  2. Advanced mode：`Course id,Teacher id,Replace Course id,Replace Teacher id`

      Example: `00874008,1001,00874008,1002`

      Selected course no. `00874008`,teacher no.`1002`,

      but wish to replace it with course no.`00874008`, teacher no.`1001`

- The courses to be selected must be valid in the system and not duplicated, or the program will run into error

- In the second mode, when the target course can be selected, the program will automatically return the course to be replaced and select the target course. Meantime, the returned course will be selected again in case that the course was selected by others.

- However, there is still possibility that both courses are failed to select, use this feature at your own risk.

- Course information items should be the form of `course`+number, you may add items like `course10=`,`course11=`... if needed.

#### **Notice**

- All configuration should be entered after the char "=" in a single line.
- It is recommended to only store encrypted password in case of leaking sensitive information.
- When `encryptpassword` is set, the program will neglect the value of `password`.
- The program will neglect invalid values in config.
- When a new term starts, you may need to change the value of `term`, or simply clear it.
- It is not recommended to log in to the course selection system elsewhere while the program is running.
- The program will be able to handle if you logged in elsewhere
- `loglevel` must be an integer between 1 and 5.
- Program logs will by default stored in `selection.log` and can be opened with a text editor.

### **Run the Program**

Run the following command

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

   `Enter the course id of course 1 :`

   Enter the 8-digit course id

   `Enter the teacher id of course 1 :`

   Enter the 4-digit teacher id

   `Do you want to replace a course you have selected with this one?`

   Enter `Y` to use Advanced Mode features or enter `N` or nothing to skip

   `Enter the course id of the course to replace :`

   Enter the 8-digit course id

   `Enter the teacher id of the course to replace :`

   Enter the 4-digit teacher id

   If you want to quit entering information, enter nothing when prompted to enter information of next course

   Please make sure that all the information you input is correct, or the program will return an error

## **Contribute**

You can star this project, create issues, discussion threads or [buy me a cup of coffee](https://ishs.gq/jz.html)

## License

Licensed under the [GPL-3.0 License](LICENSE).
