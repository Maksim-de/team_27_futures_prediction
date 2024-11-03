CREATE TABLE `news_data` (
  `news_provider` varchar(20) NOT NULL DEFAULT 'webzio' COMMENT 'API provider for the news',
  `thread_uuid` varchar(50) NOT NULL COMMENT 'Unique identifier of thread',
  `post_uuid` varchar(50) NOT NULL COMMENT 'Unique identifier of the article',
  `site` varchar(100) DEFAULT NULL COMMENT 'The top level domain of the site',
  `title` varchar(255) DEFAULT NULL COMMENT 'Article title',
  `published_timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'The date/time when the post was published.',
  `country` varchar(3) DEFAULT NULL COMMENT 'The article''s country of origin',
  `performance_score` int(11) DEFAULT NULL COMMENT 'A virality score for news and blogs posts only. The score ranges between 0-10. A score of 0 means that the post didn''t do well - it was rarely or never shared. A score of 10 means that the post was "on fire" being shared thousands of times on Facebook.',
  `domain_rank` int(11) DEFAULT NULL COMMENT 'A rank that specifies how popular a domain is',
  `language` varchar(25) DEFAULT NULL COMMENT 'The language of the post',
  `sentiment` varchar(20) DEFAULT NULL COMMENT 'Sentiment score of the article',
  `article_text` mediumtext DEFAULT NULL COMMENT 'The text body of the post',
  `request_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`post_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Table to store news data';