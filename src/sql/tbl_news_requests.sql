CREATE TABLE `news_requests` (
  `request_id` int(11) NOT NULL AUTO_INCREMENT,
  `request_text` varchar(4000) DEFAULT NULL,
  `request_datetime` datetime DEFAULT NULL,
  `api_call` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`request_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;