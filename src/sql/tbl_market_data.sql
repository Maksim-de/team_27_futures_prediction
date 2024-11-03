CREATE TABLE `market_data` (
  `open` double DEFAULT NULL,
  `high` double DEFAULT NULL,
  `low` double DEFAULT NULL,
  `close` double DEFAULT NULL,
  `adj_close` double DEFAULT NULL,
  `volume` bigint(20) DEFAULT NULL,
  `ticker` text DEFAULT NULL,
  `asset_name` varchar(255) DEFAULT NULL,
  `business_date` date DEFAULT NULL COMMENT 'Close of Business Date',
  `created_datetime` datetime DEFAULT current_timestamp() COMMENT 'Data load datetime'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;