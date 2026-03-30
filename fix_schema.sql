-- Check existing columns
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'pages_message'
ORDER BY column_name;

-- Add missing columns if they don't exist
ALTER TABLE pages_message ADD COLUMN IF NOT EXISTS sender_id integer;
ALTER TABLE pages_message ADD COLUMN IF NOT EXISTS recipient_id integer;
ALTER TABLE pages_message ADD COLUMN IF NOT EXISTS subject varchar(255);
ALTER TABLE pages_message ADD COLUMN IF NOT EXISTS body text;
ALTER TABLE pages_message ADD COLUMN IF NOT EXISTS created_at timestamp with time zone;
ALTER TABLE pages_message ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone;

-- Add foreign key constraints if they don't exist
ALTER TABLE pages_message
ADD CONSTRAINT pages_message_sender_id_fk 
FOREIGN KEY (sender_id) REFERENCES accounts_user(id) ON DELETE CASCADE;

ALTER TABLE pages_message
ADD CONSTRAINT pages_message_recipient_id_fk 
FOREIGN KEY (recipient_id) REFERENCES accounts_user(id) ON DELETE CASCADE;
