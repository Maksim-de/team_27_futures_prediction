CREATE TABLE `news_data_raw` (
  `news_provider` varchar(20) NOT NULL DEFAULT 'webzio' COMMENT 'News provider',
  `thread_uuid` varchar(50) NOT NULL COMMENT 'Unique identifier of the thread',
  `post_uuid` varchar(50) NOT NULL COMMENT 'Unique identifier of the post',
  `raw_message` mediumtext NOT NULL COMMENT 'Raw message text',
  `published_timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'The date/time when the post was published',
  `request_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`post_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Table to store raw message returned from the news provider API call';