-- 修改metadata表的resource_id列类型
ALTER TABLE seo.metadata ALTER COLUMN resource_id TYPE VARCHAR(100);

-- 验证修改结果
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'seo' AND table_name = 'metadata' AND column_name = 'resource_id';
