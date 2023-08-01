CREATE TABLE "Readability" (
    "ID" SERIAL PRIMARY KEY,
    "TimeStamp" TIMESTAMP,
    "ReadabilityScore" FLOAT(2)
);

INSERT INTO "Readability" ("TimeStamp", "ReadabilityScore")
VALUES (NOW(), 10.12);
INSERT INTO "Readability" ("TimeStamp", "ReadabilityScore")
VALUES (NOW(), 50.22);
INSERT INTO "Readability" ("TimeStamp", "ReadabilityScore")
VALUES (NOW(), 80.12);

CREATE TABLE "EmbeddingDrift" (
    "ID" SERIAL PRIMARY KEY,
    "TimeStamp" TIMESTAMP,
    "ReferenceDataset" FLOAT(3),
    "CurrentDataset" FLOAT(3),
    "Distance" FLOAT(3),
    "Drifted" BOOLEAN
);

INSERT INTO "EmbeddingDrift" ("TimeStamp", "ReferenceDataset", "CurrentDataset", "Distance", "Drifted")
VALUES (NOW(), 1.1, 1.2, 0.1, False);
INSERT INTO "EmbeddingDrift" ("TimeStamp", "ReferenceDataset", "CurrentDataset", "Distance", "Drifted")
VALUES (NOW(), 2.1, 2.2, 0.2, True);
INSERT INTO "EmbeddingDrift" ("TimeStamp", "ReferenceDataset", "CurrentDataset", "Distance", "Drifted")
VALUES (NOW(), 3.1, 3.2, 0.3, True);
