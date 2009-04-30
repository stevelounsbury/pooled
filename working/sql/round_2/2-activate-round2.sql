-- Set round 2 as the active round

begin;
update pooled_round set active=TRUE, start_date='2009-04-30 19:30:00' where id=2;
update pooled_round set active=FALSE where id=1;
commit;

