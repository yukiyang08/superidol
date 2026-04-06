ALTER TABLE public.food_records
ADD COLUMN IF NOT EXISTS photourl text,
ADD COLUMN IF NOT EXISTS photopath text,
ADD COLUMN IF NOT EXISTS photomimetype varchar(100),
ADD COLUMN IF NOT EXISTS estimatedname varchar(255),
ADD COLUMN IF NOT EXISTS estimatedcalories integer,
ADD COLUMN IF NOT EXISTS estimationprovider varchar(100),
ADD COLUMN IF NOT EXISTS estimationconfidence numeric(4,3),
ADD COLUMN IF NOT EXISTS estimationnotes text,
ADD COLUMN IF NOT EXISTS estimatedprotein numeric(8,2),
ADD COLUMN IF NOT EXISTS estimatedfat numeric(8,2),
ADD COLUMN IF NOT EXISTS estimatedcarb numeric(8,2),
ADD COLUMN IF NOT EXISTS estimatedsugar numeric(8,2),
ADD COLUMN IF NOT EXISTS estimatedsodium numeric(10,2);