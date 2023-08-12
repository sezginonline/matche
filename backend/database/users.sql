CREATE TABLE public.users (
    id BIGSERIAL PRIMARY KEY,
    email character varying NOT NULL,
    password character varying,
    name character varying,
    email_verified boolean NOT NULL DEFAULT false,
    picture character varying,
    refresh_token character varying,
    login_attempt smallint NOT NULL DEFAULT 0,
    status smallint NOT NULL DEFAULT 0,
    notes character varying,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone,
    created_ip character varying,
    updated_ip character varying
) PARTITION BY HASH (id);

CREATE INDEX users_email_idx ON public.users (email);

CREATE TABLE public.users_0 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 0);
CREATE TABLE public.users_1 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 1);
CREATE TABLE public.users_2 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 2);
CREATE TABLE public.users_3 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 3);
CREATE TABLE public.users_4 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 4);
CREATE TABLE public.users_5 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 5);
CREATE TABLE public.users_6 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 6);
CREATE TABLE public.users_7 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 7);
CREATE TABLE public.users_8 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 8);
CREATE TABLE public.users_9 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 9);
CREATE TABLE public.users_10 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 10);
CREATE TABLE public.users_11 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 11);
CREATE TABLE public.users_12 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 12);
CREATE TABLE public.users_13 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 13);
CREATE TABLE public.users_14 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 14);
CREATE TABLE public.users_15 PARTITION OF public.users FOR VALUES WITH (MODULUS 16, REMAINDER 15);
