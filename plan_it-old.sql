
CREATE TABLE `member` (
  `username` varchar(20) NOT NULL DEFAULT '',
  `password` varchar(32) NOT NULL DEFAULT '',
  `firstname` varchar(20) NOT NULL DEFAULT '',
  `lastname` varchar(20) NOT NULL DEFAULT '',
  `email` varchar(32) NOT NULL DEFAULT '',
  `zipcode` int(5) NOT NULL,
      PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `party` (
  `party_id` int(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL DEFAULT '',
  `description` text NOT NULL,
  `type_of_party` text NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `shopping_cart_id` int(20) NOT NULL,
    PRIMARY KEY (`party_id`),
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `belongs_to` (
  `party_id` int(20) NOT NULL,
  `username` varchar(20) NOT NULL DEFAULT '',
     PRIMARY KEY (`party_id`,`username`),
  FOREIGN KEY (`party_id`) REFERENCES `party` (`party_id`),
  FOREIGN KEY (`username`) REFERENCES `member` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;




CREATE TABLE `guest_list` (
  `party_id` int(20) NOT NULL,
  `guest_id` varchar(20) NOT NULL DEFAULT '',
  `status` int(1) NOT NULL,
      PRIMARY KEY (`party_id`,`guest_id`),
  FOREIGN KEY (`party_id`) REFERENCES `party` (`party_id`),
  FOREIGN KEY (`guest_id`) REFERENCES `guest` (`guest_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `guest` (
  `guest_id` int(20) NOT NULL AUTO_INCREMENT,
  `guest_name` varchar(20) NOT NULL DEFAULT '',
  `email` varchar(32) NOT NULL DEFAULT '',
      PRIMARY KEY (`guest_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `shopping_cart` (
  `shopping_cart_id` int(20) NOT NULL,
  `status` int(1) NOT NULL,
  `location_id` int(20),
      PRIMARY KEY (`shopping_cart_id`),
      FOREIGN KEY (`location_id`) REFERENCES `guest` (`location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `location` (
  `location_id` int(20) NOT NULL AUTO_INCREMENT,
  `zipcode` int(5) NOT NULL,
  `address` varchar(50) NOT NULL DEFAULT '',
  `description` text,
     PRIMARY KEY (`location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `item` (
  `item_id` int(20) NOT NULL AUTO_INCREMENT,
  `price` int(5) NOT NULL,
  `description` text,
     PRIMARY KEY (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `item_list` (
  `shopping_cart_id` int(20) NOT NULL,
  `item_id` varchar(20) NOT NULL DEFAULT '',
      PRIMARY KEY (`shopping_cart_id`,`item_id`),
  FOREIGN KEY (`shopping_cart_id`) REFERENCES `shopping_cart` (`shopping_cart_id`),
  FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;