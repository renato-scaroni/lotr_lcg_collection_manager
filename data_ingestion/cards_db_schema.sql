CREATE TABLE "Types" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "is_player_card" boolean
);

CREATE TABLE "Cycles" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "order" integer,
  "repackaged" boolean
);

CREATE TABLE "Packs" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "order_in_cycle" integer,
  "cycle_id" integer
);

CREATE TABLE "Cards" (
  "id" integer PRIMARY KEY,
  "pack" varchar,
  "name" varchar,
  "quantity" integer,
  "type_id" integer,
  "pack_id" integer,
  "sphere_name" varchar,
  "is_unique" boolean,
  "threat" integer,
  "willpower" integer,
  "attack" integer,
  "defense" integer,
  "health" integer,
  "deck_limit" integer,
  "illustrator" varchar,
  "has_errata" boolean,
  "ringsdb_url" varchar,
  "imagesrc" varchar,
  "cost" integer,
  "victory" integer,
  "quest" integer
);

CREATE TABLE "Traits" (
  "id" integer PRIMARY KEY,
  "name" varchar
);

CREATE TABLE "Cards_Traits" (
  "card_id" integer,
  "trait_id" integer
);

CREATE TABLE "Keywords" (
  "id" integer PRIMARY KEY,
  "name" varchar
);

CREATE TABLE "Cards_Keywords" (
  "card_id" integer,
  "keyword_id" integer¡
);

ALTER TABLE "Packs" ADD FOREIGN KEY ("cycle_id") REFERENCES "Cycles" ("id");

ALTER TABLE "Cards" ADD FOREIGN KEY ("type_id") REFERENCES "Types" ("id");

ALTER TABLE "Cards" ADD FOREIGN KEY ("pack_id") REFERENCES "Packs" ("id");

ALTER TABLE "Cards_Traits" ADD FOREIGN KEY ("card_id") REFERENCES "Cards" ("id");

ALTER TABLE "Cards_Traits" ADD FOREIGN KEY ("trait_id") REFERENCES "Traits" ("id");

ALTER TABLE "Cards_Keywords" ADD FOREIGN KEY ("card_id") REFERENCES "Cards" ("id");

ALTER TABLE "Cards_Keywords" ADD FOREIGN KEY ("keyword_id") REFERENCES "Keywords" ("id");