-- Arcanum 1885, after the Smoky Skies policy tree: the five scenario branches were inserted with IDs 0-4 and the three
-- Brave New World ideologies keep their stock IDs, so renumber both tables to contiguous 0..N-1 (order preserved).
CREATE TEMP TABLE ArcBranchIds AS SELECT ID AS OldID, (SELECT COUNT(*) FROM PolicyBranchTypes b2 WHERE b2.ID < b1.ID) AS NewID FROM PolicyBranchTypes b1;
UPDATE PolicyBranchTypes SET ID = (SELECT NewID FROM ArcBranchIds WHERE OldID = PolicyBranchTypes.ID) + 10000;
UPDATE PolicyBranchTypes SET ID = ID - 10000;
DROP TABLE ArcBranchIds;
CREATE TEMP TABLE ArcPolicyIds AS SELECT ID AS OldID, (SELECT COUNT(*) FROM Policies p2 WHERE p2.ID < p1.ID) AS NewID FROM Policies p1;
UPDATE Policies SET ID = (SELECT NewID FROM ArcPolicyIds WHERE OldID = Policies.ID) + 10000;
UPDATE Policies SET ID = ID - 10000;
DROP TABLE ArcPolicyIds;
