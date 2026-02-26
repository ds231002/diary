-- =====================================================
-- Extensions
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- Functions
-- =====================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Tables
-- =====================================================

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    user_name varchar NOT NULL,
    is_demo boolean DEFAULT false
);

CREATE TABLE user_profiles (
  user_id uuid PRIMARY KEY,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  first_name text,
  last_name text,
  birth_date date,
  summary text,

  CONSTRAINT fk_user_profiles_users
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE entries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  entry_date date NOT NULL DEFAULT CURRENT_DATE,
  content text NOT NULL,
  mood int,
  llm_allowed boolean NOT NULL DEFAULT true,
  embedding vector,

  CONSTRAINT chk_entries_mood_range
    CHECK (mood IS NULL OR mood BETWEEN 0 AND 10),

  CONSTRAINT uq_entries_id_user
    UNIQUE (id, user_id),
  
  CONSTRAINT fk_entries_users
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  CONSTRAINT chk_entries_embedding_llm_consistency
    CHECK (llm_allowed=true OR embedding IS NULL)
);

CREATE TABLE tags (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  name varchar NOT NULL,
  description text,
  color text,
  position int,
  favourite boolean NOT NULL DEFAULT false,
  llm_default_allowed boolean NOT NULL DEFAULT true,

  CONSTRAINT chk_tags_position
    CHECK (position IS NULL OR position >= 1),

  CONSTRAINT uq_tags_id_user
    UNIQUE (id, user_id),
  
  CONSTRAINT uq_tags_user_name
    UNIQUE (user_id, name),
  
  CONSTRAINT fk_tags_users
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE folders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  name varchar NOT NULL,
  position int,

  CONSTRAINT chk_folder_position
    CHECK (position IS NULL OR position >= 1),

  CONSTRAINT uq_folders_id_user
    UNIQUE (id, user_id),
  
  CONSTRAINT uq_folders_user_name
    UNIQUE (user_id, name),
  
  CONSTRAINT fk_folders_users
      FOREIGN KEY (user_id)
      REFERENCES users(id)
      ON DELETE CASCADE
      ON UPDATE CASCADE
);

CREATE TABLE chats (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  folder_id uuid,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  title varchar,
  start_date date,
  end_date date,
  summary text,

  CONSTRAINT chk_chats_date_range
    CHECK (end_date IS NULL OR end_date >= start_date),

  CONSTRAINT uq_chats_id_user
    UNIQUE (id, user_id),

  CONSTRAINT fk_chats_users
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_chats_folders
    FOREIGN KEY (folder_id, user_id)
    REFERENCES folders(id, user_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
);

CREATE TABLE messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id uuid NOT NULL,
  user_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  role varchar NOT NULL,
  content text NOT NULL,

  CONSTRAINT chk_messages_role
    CHECK (role IN ('user', 'assistant', 'system')),

  CONSTRAINT uq_messages_id_user
    UNIQUE (id, user_id),

  CONSTRAINT fk_messages_chat_user
    FOREIGN KEY (chat_id, user_id)
    REFERENCES chats(id, user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE entry_tags (
  entry_id uuid NOT NULL,
  tag_id uuid NOT NULL,
  user_id uuid NOT NULL,

  CONSTRAINT pk_entry_tags
    PRIMARY KEY (entry_id, tag_id),

  CONSTRAINT fk_entry_tags_entries
    FOREIGN KEY (entry_id, user_id)
    REFERENCES entries(id, user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  
  CONSTRAINT fk_entry_tags_tags
    FOREIGN KEY (tag_id, user_id)
    REFERENCES tags(id, user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE chat_tags (
  chat_id uuid NOT NULL,
  tag_id uuid NOT NULL,
  user_id uuid NOT NULL,

  CONSTRAINT pk_chat_tags
    PRIMARY KEY (chat_id, tag_id),

  CONSTRAINT fk_chat_tags_chats
    FOREIGN KEY (chat_id, user_id)
    REFERENCES chats(id, user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_chat_tags_tags
    FOREIGN KEY (tag_id, user_id)
    REFERENCES tags(id, user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- =====================================================
-- Triggers
-- =====================================================

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_user_profiles_updated_at
BEFORE UPDATE ON user_profiles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_entries_updated_at
BEFORE UPDATE ON entries
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_tags_updated_at
BEFORE UPDATE ON tags
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_folders_updated_at
BEFORE UPDATE ON folders
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_chats_updated_at
BEFORE UPDATE ON chats
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();