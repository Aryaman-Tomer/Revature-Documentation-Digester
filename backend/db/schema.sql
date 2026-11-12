-- Schema for the user stories that search retrieves against a question.
-- Safe to run more than once.

CREATE TABLE IF NOT EXISTS user_stories (
    id                  SERIAL       PRIMARY KEY,
    title               VARCHAR(200) NOT NULL UNIQUE,
    story               TEXT         NOT NULL,
    acceptance_criteria TEXT         NOT NULL,
    source              VARCHAR(255) NOT NULL
);

COMMENT ON COLUMN user_stories.story IS 'The "As a ..., I want ..., so that ..." text.';
COMMENT ON COLUMN user_stories.source IS 'Sample doc (under data/samples) the story is based on.';
