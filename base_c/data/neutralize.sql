-- executed when backup from SH prod
-- set ribbon
UPDATE ir_config_parameter SET value = 'TEST' WHERE key = 'ribbon.name' ;
