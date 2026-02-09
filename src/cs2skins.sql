-- public.cs2_skins definition

-- Drop table

-- DROP TABLE public.cs2_skins;

CREATE TABLE public.cs2_skins (
	"name" text NOT NULL,
	price numeric(10, 2) NOT NULL,
	updated int8 DEFAULT EXTRACT(epoch FROM now()) NOT NULL,
	skin varchar NULL,
	wear varchar NULL,
	CONSTRAINT cs2_skins_pkey PRIMARY KEY (name)
);
CREATE INDEX cs2_skins_skin_idx ON public.cs2_skins USING btree (skin, wear, name);
CREATE INDEX cs2_skins_wear_idx ON public.cs2_skins USING btree (wear);

-- Table Triggers

create trigger set_updated_unix before
update
    on
    public.cs2_skins for each row execute function set_updated_unix();