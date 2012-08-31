SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `pyradio` DEFAULT CHARACTER SET utf8 ;
USE `pyradio` ;

-- -----------------------------------------------------
-- Table `pyradio`.`users`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`users` (
  `user` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(50) NOT NULL ,
  `password` VARCHAR(128) NOT NULL ,
  `streampassword` VARCHAR(128) NOT NULL ,
  `status` INT UNSIGNED NULL DEFAULT 0 ,
  PRIMARY KEY (`user`) ,
  UNIQUE INDEX `name` (`name` ASC) )
ENGINE = InnoDB
AUTO_INCREMENT = 593
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`apikeys`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`apikeys` (
  `apikey` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `user` INT UNSIGNED NOT NULL ,
  `application` VARCHAR(128) NOT NULL ,
  `description` TEXT NULL DEFAULT NULL ,
  `key` VARCHAR(128) NOT NULL ,
  `counter` INT UNSIGNED NOT NULL DEFAULT 0 ,
  `access` DATETIME NOT NULL ,
  `flag` INT UNSIGNED NOT NULL DEFAULT 0 ,
  PRIMARY KEY (`apikey`) ,
  UNIQUE INDEX `key` (`key` ASC) ,
  INDEX `user` (`user` ASC) ,
  CONSTRAINT `apikeys_ibfk_1`
    FOREIGN KEY (`user` )
    REFERENCES `pyradio`.`users` (`user` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`artists`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`artists` (
  `artist` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(255) NOT NULL ,
  `flags` INT UNSIGNED NULL DEFAULT NULL ,
  PRIMARY KEY (`artist`) )
ENGINE = InnoDB
AUTO_INCREMENT = 19575
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`ircusers`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`ircusers` (
  `ircuser` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `user` INT UNSIGNED NOT NULL ,
  `hostmask` VARCHAR(255) NOT NULL ,
  PRIMARY KEY (`ircuser`) ,
  INDEX `user` (`user` ASC) ,
  CONSTRAINT `ircusers_ibfk_1`
    FOREIGN KEY (`user` )
    REFERENCES `pyradio`.`users` (`user` )
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`relays`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`relays` (
  `relay` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(50) NOT NULL ,
  `hostname` VARCHAR(128) NOT NULL ,
  `port` INT UNSIGNED NOT NULL ,
  `type` INT UNSIGNED NOT NULL ,
  `bandwidth` INT UNSIGNED NOT NULL ,
  `traffic` INT UNSIGNED NULL ,
  `status` INT UNSIGNED NOT NULL ,
  `queryMethod` INT UNSIGNED NOT NULL ,
  `queryUsername` VARCHAR(50) NOT NULL ,
  `queryPassword` VARCHAR(50) NOT NULL ,
  PRIMARY KEY (`relay`) ,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) )
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`streams`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`streams` (
  `stream` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `mountpoint` VARCHAR(50) NOT NULL ,
  `name` VARCHAR(50) NOT NULL ,
  `description` VARCHAR(50) NOT NULL ,
  `type` INT UNSIGNED NOT NULL ,
  `quality` INT NOT NULL ,
  `username` VARCHAR(50) NOT NULL ,
  `password` VARCHAR(50) NOT NULL ,
  PRIMARY KEY (`stream`) )
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`listeners`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`listeners` (
  `listener` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `disconnect` DATETIME NULL ,
  `connect` DATETIME NULL DEFAULT NULL ,
  `address` INT UNSIGNED NOT NULL ,
  `useragent` VARCHAR(255) NOT NULL ,
  `relay` INT UNSIGNED NOT NULL ,
  `stream` INT UNSIGNED NOT NULL ,
  `client` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`listener`) ,
  INDEX `relay` (`relay` ASC) ,
  INDEX `stream` (`stream` ASC) ,
  CONSTRAINT `listeners_ibfk_1`
    FOREIGN KEY (`relay` )
    REFERENCES `pyradio`.`relays` (`relay` )
    ON UPDATE CASCADE,
  CONSTRAINT `listeners_ibfk_2`
    FOREIGN KEY (`stream` )
    REFERENCES `pyradio`.`streams` (`stream` )
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 349178
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`metaArtists`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`metaArtists` (
  `metaArtist` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `artist` INT UNSIGNED NOT NULL ,
  `name` VARCHAR(255) NOT NULL ,
  PRIMARY KEY (`metaArtist`) ,
  UNIQUE INDEX `name` (`name` ASC) ,
  INDEX `artist` (`artist` ASC) ,
  CONSTRAINT `metaArtists_ibfk_1`
    FOREIGN KEY (`artist` )
    REFERENCES `pyradio`.`artists` (`artist` )
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 19575
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`titles`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`titles` (
  `title` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `artist` INT UNSIGNED NOT NULL ,
  `name` VARCHAR(255) NOT NULL ,
  `duration` INT UNSIGNED NOT NULL ,
  `flags` INT UNSIGNED NULL ,
  PRIMARY KEY (`title`) ,
  INDEX `artist` (`artist` ASC) ,
  CONSTRAINT `titles_ibfk_1`
    FOREIGN KEY (`artist` )
    REFERENCES `pyradio`.`artists` (`artist` )
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 58738
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`metaTitles`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`metaTitles` (
  `metaTitle` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `title` INT UNSIGNED NOT NULL ,
  `name` VARCHAR(255) NOT NULL ,
  `duration` INT UNSIGNED NOT NULL ,
  `durationWeight` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`metaTitle`) ,
  INDEX `title` (`title` ASC) ,
  CONSTRAINT `metaTitles_ibfk_1`
    FOREIGN KEY (`title` )
    REFERENCES `pyradio`.`titles` (`title` )
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 58738
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`news`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`news` (
  `news` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `time` DATETIME NOT NULL ,
  `user` INT UNSIGNED NOT NULL ,
  `title` VARCHAR(255) NOT NULL ,
  `content` TEXT NOT NULL ,
  PRIMARY KEY (`news`) ,
  INDEX `user` (`user` ASC) ,
  CONSTRAINT `news_ibfk_1`
    FOREIGN KEY (`user` )
    REFERENCES `pyradio`.`users` (`user` )
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 13
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`playlist`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`playlist` (
  `playlist` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `begin` TIME NOT NULL ,
  `end` TIME NOT NULL ,
  `file` VARCHAR(128) NOT NULL ,
  PRIMARY KEY (`playlist`) )
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`series`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`series` (
  `series` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(50) NOT NULL ,
  `description` TEXT NULL DEFAULT NULL ,
  PRIMARY KEY (`series`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`shows`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`shows` (
  `show` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `series` INT UNSIGNED NULL DEFAULT NULL ,
  `begin` DATETIME NOT NULL ,
  `end` DATETIME NOT NULL ,
  `name` VARCHAR(50) NOT NULL ,
  `description` TEXT NOT NULL ,
  `flags` INT UNSIGNED NOT NULL DEFAULT 0 ,
  `updated` DATETIME NOT NULL ,
  PRIMARY KEY (`show`) ,
  INDEX `series` (`series` ASC) ,
  CONSTRAINT `shows_ibfk_1`
    FOREIGN KEY (`series` )
    REFERENCES `pyradio`.`series` (`series` )
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 8633
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`show_listener`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`show_listener` (
  `show` INT UNSIGNED NOT NULL ,
  `listener` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`show`, `listener`) ,
  INDEX `listener` (`listener` ASC) ,
  CONSTRAINT `show_listener_ibfk_1`
    FOREIGN KEY (`show` )
    REFERENCES `pyradio`.`shows` (`show` )
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `show_listener_ibfk_2`
    FOREIGN KEY (`listener` )
    REFERENCES `pyradio`.`listeners` (`listener` ))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`tags`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`tags` (
  `tag` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(50) NOT NULL ,
  PRIMARY KEY (`tag`) ,
  UNIQUE INDEX `name` (`name` ASC) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`show_tags`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`show_tags` (
  `show` INT UNSIGNED NOT NULL ,
  `tag` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`show`, `tag`) ,
  INDEX `tag` (`tag` ASC) ,
  CONSTRAINT `show_tags_ibfk_1`
    FOREIGN KEY (`show` )
    REFERENCES `pyradio`.`shows` (`show` )
    ON UPDATE RESTRICT,
  CONSTRAINT `show_tags_ibfk_2`
    FOREIGN KEY (`tag` )
    REFERENCES `pyradio`.`tags` (`tag` ))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`songs`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`songs` (
  `song` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `begin` DATETIME NOT NULL ,
  `end` DATETIME NULL DEFAULT NULL ,
  `title` INT UNSIGNED NOT NULL ,
  `show` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`song`) ,
  INDEX `title` (`title` ASC) ,
  INDEX `show` (`show` ASC) ,
  CONSTRAINT `songs_ibfk_1`
    FOREIGN KEY (`title` )
    REFERENCES `pyradio`.`titles` (`title` )
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `songs_ibfk_2`
    FOREIGN KEY (`show` )
    REFERENCES `pyradio`.`shows` (`show` )
    ON UPDATE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 96068
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`stream_relays`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`stream_relays` (
  `stream` INT UNSIGNED NOT NULL ,
  `relay` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`stream`, `relay`) ,
  INDEX `relay` (`relay` ASC) ,
  CONSTRAINT `stream_relays_ibfk_1`
    FOREIGN KEY (`stream` )
    REFERENCES `pyradio`.`streams` (`stream` )
    ON UPDATE RESTRICT,
  CONSTRAINT `stream_relays_ibfk_2`
    FOREIGN KEY (`relay` )
    REFERENCES `pyradio`.`relays` (`relay` ))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`user_shows`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`user_shows` (
  `user` INT UNSIGNED NOT NULL ,
  `show` INT UNSIGNED NOT NULL ,
  `role` INT UNSIGNED NULL DEFAULT NULL ,
  PRIMARY KEY (`user`, `show`) ,
  INDEX `show` (`show` ASC) ,
  CONSTRAINT `user_shows_ibfk_1`
    FOREIGN KEY (`user` )
    REFERENCES `pyradio`.`users` (`user` )
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `user_shows_ibfk_2`
    FOREIGN KEY (`show` )
    REFERENCES `pyradio`.`shows` (`show` ))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `pyradio`.`settings`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`settings` (
  `setting` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `code` CHAR(20) NOT NULL ,
  `name` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`setting`) ,
  UNIQUE INDEX `code_UNIQUE` (`code` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pyradio`.`user_settings`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`user_settings` (
  `user` INT UNSIGNED NOT NULL ,
  `setting` INT UNSIGNED NOT NULL ,
  `value` VARCHAR(255) NOT NULL ,
  PRIMARY KEY (`user`, `setting`) ,
  INDEX `fk_users_users` (`user` ASC) ,
  INDEX `fk_users_settings` (`setting` ASC) ,
  CONSTRAINT `fk_settings_has_users_settings1`
    FOREIGN KEY (`setting` )
    REFERENCES `pyradio`.`settings` (`setting` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_settings_has_users_users1`
    FOREIGN KEY (`user` )
    REFERENCES `pyradio`.`users` (`user` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pyradio`.`permissions`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`permissions` (
  `permission` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
  `code` CHAR(20) NOT NULL ,
  `name` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`permission`) ,
  UNIQUE INDEX `code_UNIQUE` (`code` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `pyradio`.`user_permissions`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `pyradio`.`user_permissions` (
  `permission` INT UNSIGNED NOT NULL ,
  `user` INT UNSIGNED NOT NULL ,
  PRIMARY KEY (`permission`, `user`) ,
  INDEX `fk_users_users` (`user` ASC) ,
  INDEX `fk_users_permissions` (`permission` ASC) ,
  CONSTRAINT `fk_users_permissions`
    FOREIGN KEY (`permission` )
    REFERENCES `pyradio`.`permissions` (`permission` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_users`
    FOREIGN KEY (`user` )
    REFERENCES `pyradio`.`users` (`user` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

