-- Notes and ALTER statements for Round 2 data migration.

-- Manage.py stuff
-- Must drop and recreate rounds table with syncdb.

-- Add round reference to leaderboardstat
BEGIN;
ALTER TABLE `pooled_leaderboardstat` ADD `round_id` integer NOT NULL AFTER pool_id;
ALTER TABLE `pooled_leaderboardstat` ADD `is_final` bool NOT NULL AFTER `current`;
UPDATE pooled_leaderboardstat SET round_id=1;
UPDATE pooled_leaderboardstat SET is_final=TRUE WHERE current=TRUE;
UPDATE pooled_pickround SET current_round_id=2, start_date="2009-04-29 00:00:01", end_date="2009-05-01 00:00:01", can_pick_cup=FALSE;
COMMIT;
