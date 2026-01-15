/*
 Navicat Premium Dump SQL

 Source Server         : MySQL
 Source Server Type    : MySQL
 Source Server Version : 80043 (8.0.43)
 Source Host           : localhost:3306
 Source Schema         : educational_management_system

 Target Server Type    : MySQL
 Target Server Version : 80043 (8.0.43)
 File Encoding         : 65001

 Date: 15/01/2026 21:29:47
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for classes
-- ----------------------------
DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes`  (
  `class_id` int NOT NULL AUTO_INCREMENT COMMENT '班级ID',
  `class_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '班级名称',
  `major_id` int NOT NULL COMMENT '所属专业ID',
  `grade` year NOT NULL COMMENT '年级',
  PRIMARY KEY (`class_id`) USING BTREE,
  UNIQUE INDEX `uk_class`(`class_name` ASC, `grade` ASC) USING BTREE,
  INDEX `major_id`(`major_id` ASC) USING BTREE,
  CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`major_id`) REFERENCES `majors` (`major_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '班级信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for course_arrangements
-- ----------------------------
DROP TABLE IF EXISTS `course_arrangements`;
CREATE TABLE `course_arrangements`  (
  `arrangement_id` int NOT NULL AUTO_INCREMENT COMMENT '排课ID（主键，自增）',
  `course_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程编号',
  `teacher_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '教师工号',
  `semester` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学期（如2026-2027-1）',
  `class_id` int NOT NULL COMMENT '授课班级ID',
  `week` int NULL DEFAULT 0 COMMENT '周次（1-18）',
  `day` int NULL DEFAULT 0 COMMENT '星期几（1-7）',
  `period` int NULL DEFAULT 0 COMMENT '节次（1-10）',
  `classroom` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '' COMMENT '教室',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '排课时间',
  PRIMARY KEY (`arrangement_id`) USING BTREE,
  INDEX `course_id`(`course_id` ASC) USING BTREE,
  INDEX `teacher_id`(`teacher_id` ASC) USING BTREE,
  INDEX `class_id`(`class_id` ASC) USING BTREE,
  CONSTRAINT `course_arrangements_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `course_arrangements_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `course_arrangements_ibfk_3` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课程安排表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `course_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程编号',
  `course_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程名称',
  `credit` float NOT NULL COMMENT '学分',
  `hours` int NOT NULL COMMENT '课时',
  `type` enum('必修课','选修课') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程类型',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`course_id`) USING BTREE,
  CONSTRAINT `chk_course_credit` CHECK (`credit` >= 0),
  CONSTRAINT `chk_course_hours` CHECK (`hours` >= 0)
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课程信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for departments
-- ----------------------------
DROP TABLE IF EXISTS `departments`;
CREATE TABLE `departments`  (
  `dept_id` int NOT NULL AUTO_INCREMENT COMMENT '院系ID',
  `dept_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '院系名称（如：计算机学院、文学院）',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`dept_id`) USING BTREE,
  UNIQUE INDEX `uk_dept_name`(`dept_name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '院系信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for majors
-- ----------------------------
DROP TABLE IF EXISTS `majors`;
CREATE TABLE `majors`  (
  `major_id` int NOT NULL AUTO_INCREMENT COMMENT '专业ID',
  `major_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '专业名称',
  `dept_id` int NOT NULL COMMENT '所属院系ID',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`major_id`) USING BTREE,
  INDEX `fk_major_dept`(`dept_id` ASC) USING BTREE,
  CONSTRAINT `fk_major_dept` FOREIGN KEY (`dept_id`) REFERENCES `departments` (`dept_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '专业信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for scores
-- ----------------------------
DROP TABLE IF EXISTS `scores`;
CREATE TABLE `scores`  (
  `score_id` int NOT NULL AUTO_INCREMENT COMMENT '成绩ID',
  `student_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生ID',
  `course_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程ID',
  `semester` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学期',
  `score` float NULL DEFAULT NULL COMMENT '分数',
  `grade` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '等级（优秀/良好/及格/不及格）',
  `teacher_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '评分教师ID',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '录入时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`score_id`) USING BTREE,
  UNIQUE INDEX `uk_score`(`student_id` ASC, `course_id` ASC, `semester` ASC) USING BTREE,
  INDEX `course_id`(`course_id` ASC) USING BTREE,
  INDEX `teacher_id`(`teacher_id` ASC) USING BTREE,
  CONSTRAINT `scores_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `scores_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `scores_ibfk_3` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `chk_score_range` CHECK ((`score` >= 0) and (`score` <= 100))
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '成绩表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for students
-- ----------------------------
DROP TABLE IF EXISTS `students`;
CREATE TABLE `students`  (
  `student_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学号',
  `student_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `gender` enum('男','女') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '性别',
  `birth_date` date NULL DEFAULT NULL COMMENT '出生日期',
  `class_id` int NOT NULL COMMENT '所属班级ID',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '联系电话',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '邮箱',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`student_id`) USING BTREE,
  INDEX `class_id`(`class_id` ASC) USING BTREE,
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `chk_student_phone` CHECK (regexp_like(`phone`,_utf8mb4'^$|^1[0-9]{10}$'))
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for teachers
-- ----------------------------
DROP TABLE IF EXISTS `teachers`;
CREATE TABLE `teachers`  (
  `teacher_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '教师工号',
  `teacher_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `gender` enum('男','女') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '性别',
  `dept_id` int NOT NULL COMMENT '所属院系ID',
  `title` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '职称',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '联系电话',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '邮箱',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`teacher_id`) USING BTREE,
  INDEX `fk_teacher_dept`(`dept_id` ASC) USING BTREE,
  CONSTRAINT `fk_teacher_dept` FOREIGN KEY (`dept_id`) REFERENCES `departments` (`dept_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `chk_teacher_phone` CHECK (regexp_like(`phone`,_utf8mb4'^$|^1[0-9]{10}$'))
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '教师信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码（加密存储）',
  `role` enum('admin','teacher','student') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色',
  `related_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联ID（学生号/教师工号）',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `uk_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for v_classes
-- ----------------------------
DROP VIEW IF EXISTS `v_classes`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_classes` AS select `c`.`class_id` AS `class_id`,`c`.`class_name` AS `class_name`,`c`.`major_id` AS `major_id`,`c`.`grade` AS `grade`,`m`.`major_name` AS `major_name`,`d`.`dept_name` AS `dept_name` from ((`classes` `c` left join `majors` `m` on((`c`.`major_id` = `m`.`major_id`))) left join `departments` `d` on((`m`.`dept_id` = `d`.`dept_id`)));

-- ----------------------------
-- View structure for v_course_arrangements
-- ----------------------------
DROP VIEW IF EXISTS `v_course_arrangements`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_course_arrangements` AS select `ca`.`arrangement_id` AS `arrangement_id`,`ca`.`course_id` AS `course_id`,`c`.`course_name` AS `course_name`,`c`.`credit` AS `credit`,`c`.`hours` AS `hours`,`c`.`type` AS `type`,`ca`.`teacher_id` AS `teacher_id`,`t`.`teacher_name` AS `teacher_name`,`ca`.`class_id` AS `class_id`,`cl`.`class_name` AS `class_name`,`cl`.`grade` AS `grade`,`ca`.`semester` AS `semester`,`ca`.`week` AS `week`,`ca`.`day` AS `day`,`ca`.`period` AS `period`,`ca`.`classroom` AS `classroom` from (((`course_arrangements` `ca` left join `courses` `c` on((`ca`.`course_id` = `c`.`course_id`))) left join `teachers` `t` on((`ca`.`teacher_id` = `t`.`teacher_id`))) left join `classes` `cl` on((`ca`.`class_id` = `cl`.`class_id`)));

-- ----------------------------
-- View structure for v_majors
-- ----------------------------
DROP VIEW IF EXISTS `v_majors`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_majors` AS select `m`.`major_id` AS `major_id`,`m`.`major_name` AS `major_name`,`m`.`dept_id` AS `dept_id`,`m`.`create_time` AS `create_time`,`d`.`dept_name` AS `dept_name` from (`majors` `m` left join `departments` `d` on((`m`.`dept_id` = `d`.`dept_id`)));

-- ----------------------------
-- View structure for v_student_courses
-- ----------------------------
DROP VIEW IF EXISTS `v_student_courses`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_student_courses` AS select `ca`.`arrangement_id` AS `arrangement_id`,`ca`.`course_id` AS `course_id`,`c`.`course_name` AS `course_name`,`c`.`credit` AS `credit`,`c`.`hours` AS `hours`,`c`.`type` AS `type`,`t`.`teacher_id` AS `teacher_id`,`t`.`teacher_name` AS `teacher_name`,`cl`.`class_id` AS `class_id`,`cl`.`class_name` AS `class_name`,`ca`.`semester` AS `semester`,`ca`.`week` AS `week`,`ca`.`day` AS `day`,`ca`.`period` AS `period`,`ca`.`classroom` AS `classroom`,`s`.`student_id` AS `student_id` from ((((`course_arrangements` `ca` left join `courses` `c` on((`ca`.`course_id` = `c`.`course_id`))) left join `teachers` `t` on((`ca`.`teacher_id` = `t`.`teacher_id`))) left join `classes` `cl` on((`ca`.`class_id` = `cl`.`class_id`))) left join `students` `s` on((`cl`.`class_id` = `s`.`class_id`)));

-- ----------------------------
-- View structure for v_student_timetable
-- ----------------------------
DROP VIEW IF EXISTS `v_student_timetable`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_student_timetable` AS select `ca`.`arrangement_id` AS `arrangement_id`,`ca`.`course_id` AS `course_id`,`c`.`course_name` AS `course_name`,`c`.`credit` AS `credit`,`c`.`hours` AS `hours`,`c`.`type` AS `type`,`ca`.`teacher_id` AS `teacher_id`,`t`.`teacher_name` AS `teacher_name`,`s`.`student_id` AS `student_id`,`s`.`student_name` AS `student_name`,`cl`.`class_id` AS `class_id`,`cl`.`class_name` AS `class_name`,`ca`.`semester` AS `semester`,`ca`.`week` AS `week`,`ca`.`day` AS `day`,`ca`.`period` AS `period`,`ca`.`classroom` AS `classroom` from ((((`course_arrangements` `ca` left join `courses` `c` on((`ca`.`course_id` = `c`.`course_id`))) left join `teachers` `t` on((`ca`.`teacher_id` = `t`.`teacher_id`))) left join `classes` `cl` on((`ca`.`class_id` = `cl`.`class_id`))) left join `students` `s` on((`cl`.`class_id` = `s`.`class_id`)));

-- ----------------------------
-- View structure for v_students
-- ----------------------------
DROP VIEW IF EXISTS `v_students`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_students` AS select `s`.`student_id` AS `student_id`,`s`.`student_name` AS `student_name`,`s`.`gender` AS `gender`,`s`.`birth_date` AS `birth_date`,`s`.`class_id` AS `class_id`,`s`.`phone` AS `phone`,`s`.`email` AS `email`,`s`.`create_time` AS `create_time`,`c`.`class_name` AS `class_name`,`m`.`major_name` AS `major_name`,`d`.`dept_name` AS `dept_name` from (((`students` `s` left join `classes` `c` on((`s`.`class_id` = `c`.`class_id`))) left join `majors` `m` on((`c`.`major_id` = `m`.`major_id`))) left join `departments` `d` on((`m`.`dept_id` = `d`.`dept_id`)));

-- ----------------------------
-- View structure for v_teachers
-- ----------------------------
DROP VIEW IF EXISTS `v_teachers`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_teachers` AS select `t`.`teacher_id` AS `teacher_id`,`t`.`teacher_name` AS `teacher_name`,`t`.`gender` AS `gender`,`t`.`dept_id` AS `dept_id`,`t`.`title` AS `title`,`t`.`phone` AS `phone`,`t`.`email` AS `email`,`t`.`create_time` AS `create_time`,`d`.`dept_name` AS `dept_name` from (`teachers` `t` left join `departments` `d` on((`t`.`dept_id` = `d`.`dept_id`)));

-- ----------------------------
-- Triggers structure for table courses
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_deny_delete_course_with_score`;
delimiter ;;
CREATE TRIGGER `trg_deny_delete_course_with_score` BEFORE DELETE ON `courses` FOR EACH ROW BEGIN
    IF EXISTS (SELECT 1 FROM scores WHERE course_id = OLD.course_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '该课程已有成绩记录，禁止删除！';
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table scores
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_score_grade`;
delimiter ;;
CREATE TRIGGER `trg_score_grade` BEFORE INSERT ON `scores` FOR EACH ROW BEGIN
    -- 根据分数判断等级
    IF NEW.score >= 90 THEN
        SET NEW.grade = '优秀';
    ELSEIF NEW.score >= 80 THEN
        SET NEW.grade = '良好';
    ELSEIF NEW.score >= 60 THEN
        SET NEW.grade = '及格';
    ELSEIF NEW.score IS NOT NULL THEN
        SET NEW.grade = '不及格';
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table scores
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_score_grade_update`;
delimiter ;;
CREATE TRIGGER `trg_score_grade_update` BEFORE UPDATE ON `scores` FOR EACH ROW BEGIN
    IF NEW.score != OLD.score THEN  -- 只有分数变化时才更新等级
        IF NEW.score >= 90 THEN
            SET NEW.grade = '优秀';
        ELSEIF NEW.score >= 80 THEN
            SET NEW.grade = '良好';
        ELSEIF NEW.score >= 60 THEN
            SET NEW.grade = '及格';
        ELSEIF NEW.score IS NOT NULL THEN
            SET NEW.grade = '不及格';
        END IF;
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table scores
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_score_insert_log`;
delimiter ;;
CREATE TRIGGER `trg_score_insert_log` AFTER INSERT ON `scores` FOR EACH ROW BEGIN
    -- 插入日志（new_value存新增的成绩信息，old_value为空）
    INSERT INTO operation_logs (
        operator_id, operator_role, operation_type, table_name, 
        record_id, new_value
    ) VALUES (
        NEW.teacher_id, 'teacher', 'INSERT', 'scores',
        NEW.score_id, 
        CONCAT('{"student_id":"', NEW.student_id, '","course_id":"', NEW.course_id, '","semester":"', NEW.semester, '","score":', NEW.score, ',"grade":"', NEW.grade, '"}')
    );
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table scores
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_score_update_log`;
delimiter ;;
CREATE TRIGGER `trg_score_update_log` AFTER UPDATE ON `scores` FOR EACH ROW BEGIN
    -- 记录修改前后的值
    INSERT INTO operation_logs (
        operator_id, operator_role, operation_type, table_name, 
        record_id, old_value, new_value
    ) VALUES (
        NEW.teacher_id, 'teacher', 'UPDATE', 'scores',
        NEW.score_id,
        -- 旧值
        CONCAT('{"score":', OLD.score, ',"grade":"', OLD.grade, '"}'),
        -- 新值
        CONCAT('{"score":', NEW.score, ',"grade":"', NEW.grade, '"}')
    );
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table students
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_deny_delete_student_with_score`;
delimiter ;;
CREATE TRIGGER `trg_deny_delete_student_with_score` BEFORE DELETE ON `students` FOR EACH ROW BEGIN
    -- 查询该学生是否有成绩
    IF EXISTS (SELECT 1 FROM scores WHERE student_id = OLD.student_id) THEN
        -- 抛出错误，阻止删除
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '该学生已有成绩记录，禁止删除！';
    END IF;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table students
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_student_after_insert`;
delimiter ;;
CREATE TRIGGER `trg_student_after_insert` AFTER INSERT ON `students` FOR EACH ROW BEGIN
    -- 插入user表：用户名=学号，密码=123456（MD5加密），角色=student
    INSERT IGNORE INTO users (
        username, 
        password, 
        role, 
        related_id
    ) VALUES (
        NEW.student_id, 
        'e10adc3949ba59abbe56e057f20f883e',  -- 123456的MD5
        'student', 
        NEW.student_id
    );
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table students
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_student_after_delete`;
delimiter ;;
CREATE TRIGGER `trg_student_after_delete` AFTER DELETE ON `students` FOR EACH ROW BEGIN
    -- 根据学号+学生角色删除用户
    DELETE FROM users 
    WHERE username = OLD.student_id 
      AND role = 'student' 
      AND related_id = OLD.student_id;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table teachers
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_teacher_after_insert`;
delimiter ;;
CREATE TRIGGER `trg_teacher_after_insert` AFTER INSERT ON `teachers` FOR EACH ROW BEGIN
    -- 插入user表：用户名=工号，密码=123456（MD5加密），角色=teacher
    INSERT IGNORE INTO users (
        username,
        password,
        role,
        related_id
    ) VALUES (
        NEW.teacher_id,
        'e10adc3949ba59abbe56e057f20f883e',  -- 123456的MD5值（修正拼写错误）
        'teacher',
        NEW.teacher_id
    );
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table teachers
-- ----------------------------
DROP TRIGGER IF EXISTS `trg_teacher_after_delete`;
delimiter ;;
CREATE TRIGGER `trg_teacher_after_delete` AFTER DELETE ON `teachers` FOR EACH ROW BEGIN
    -- 根据工号+教师角色删除用户
    DELETE FROM users 
    WHERE username = OLD.teacher_id 
      AND role = 'teacher' 
      AND related_id = OLD.teacher_id;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
