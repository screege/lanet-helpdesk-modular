--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2025-07-20 20:26:20

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS lanet_helpdesk;
--
-- TOC entry 5789 (class 1262 OID 33830)
-- Name: lanet_helpdesk; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE lanet_helpdesk WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Spanish_Mexico.1252';


ALTER DATABASE lanet_helpdesk OWNER TO postgres;

\connect lanet_helpdesk

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3 (class 3079 OID 33842)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5791 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- TOC entry 2 (class 3079 OID 33831)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5792 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 969 (class 1247 OID 33950)
-- Name: agent_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.agent_status AS ENUM (
    'online',
    'offline',
    'maintenance',
    'error'
);


ALTER TYPE public.agent_status OWNER TO postgres;

--
-- TOC entry 966 (class 1247 OID 33932)
-- Name: asset_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.asset_type AS ENUM (
    'desktop',
    'laptop',
    'server',
    'printer',
    'network_device',
    'mobile_device',
    'software',
    'other'
);


ALTER TYPE public.asset_type OWNER TO postgres;

--
-- TOC entry 963 (class 1247 OID 33922)
-- Name: ticket_channel; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticket_channel AS ENUM (
    'portal',
    'email',
    'agente',
    'telefono'
);


ALTER TYPE public.ticket_channel OWNER TO postgres;

--
-- TOC entry 957 (class 1247 OID 33892)
-- Name: ticket_priority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticket_priority AS ENUM (
    'baja',
    'media',
    'alta',
    'critica'
);


ALTER TYPE public.ticket_priority OWNER TO postgres;

--
-- TOC entry 960 (class 1247 OID 33902)
-- Name: ticket_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticket_status AS ENUM (
    'nuevo',
    'asignado',
    'en_proceso',
    'espera_cliente',
    'resuelto',
    'cerrado',
    'cancelado',
    'pendiente_aprobacion',
    'reabierto'
);


ALTER TYPE public.ticket_status OWNER TO postgres;

--
-- TOC entry 954 (class 1247 OID 33880)
-- Name: user_role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role AS ENUM (
    'superadmin',
    'admin',
    'technician',
    'client_admin',
    'solicitante'
);


ALTER TYPE public.user_role OWNER TO postgres;

--
-- TOC entry 329 (class 1255 OID 34402)
-- Name: audit_trigger_function(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, timestamp)
        VALUES (
            current_setting('app.current_user_id', true)::UUID,
            'DELETE',
            TG_TABLE_NAME,
            OLD.client_id, -- Assuming most tables have client_id
            row_to_json(OLD),
            CURRENT_TIMESTAMP
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values, timestamp)
        VALUES (
            current_setting('app.current_user_id', true)::UUID,
            'UPDATE',
            TG_TABLE_NAME,
            NEW.client_id, -- Assuming most tables have client_id
            row_to_json(OLD),
            row_to_json(NEW),
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (user_id, action, table_name, record_id, new_values, timestamp)
        VALUES (
            current_setting('app.current_user_id', true)::UUID,
            'INSERT',
            TG_TABLE_NAME,
            NEW.client_id, -- Assuming most tables have client_id
            row_to_json(NEW),
            CURRENT_TIMESTAMP
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_trigger_function() OWNER TO postgres;

--
-- TOC entry 327 (class 1255 OID 34419)
-- Name: current_user_client_id(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.current_user_client_id() RETURNS uuid
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    RETURN current_setting('app.current_user_client_id', true)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$;


ALTER FUNCTION public.current_user_client_id() OWNER TO postgres;

--
-- TOC entry 325 (class 1255 OID 34417)
-- Name: current_user_id(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.current_user_id() RETURNS uuid
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    RETURN current_setting('app.current_user_id', true)::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$;


ALTER FUNCTION public.current_user_id() OWNER TO postgres;

--
-- TOC entry 326 (class 1255 OID 34418)
-- Name: current_user_role(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.current_user_role() RETURNS public.user_role
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    RETURN current_setting('app.current_user_role', true)::user_role;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$;


ALTER FUNCTION public.current_user_role() OWNER TO postgres;

--
-- TOC entry 328 (class 1255 OID 34420)
-- Name: current_user_site_ids(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.current_user_site_ids() RETURNS uuid[]
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    RETURN string_to_array(current_setting('app.current_user_site_ids', true), ',')::UUID[];
EXCEPTION
    WHEN OTHERS THEN
        RETURN ARRAY[]::UUID[];
END;
$$;


ALTER FUNCTION public.current_user_site_ids() OWNER TO postgres;

--
-- TOC entry 332 (class 1255 OID 37104)
-- Name: ensure_single_primary_site(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.ensure_single_primary_site() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- If setting a site as primary, unset all other primary sites for this client
    IF NEW.is_primary_site = true THEN
        UPDATE sites 
        SET is_primary_site = false 
        WHERE client_id = NEW.client_id 
        AND site_id != NEW.site_id;
    END IF;
    
    -- If no primary site exists for client, make this one primary
    IF NOT EXISTS (
        SELECT 1 FROM sites 
        WHERE client_id = NEW.client_id 
        AND is_primary_site = true 
        AND site_id != NEW.site_id
    ) THEN
        NEW.is_primary_site = true;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.ensure_single_primary_site() OWNER TO postgres;

--
-- TOC entry 336 (class 1255 OID 37736)
-- Name: generate_agent_token(uuid, uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.generate_agent_token(p_client_id uuid, p_site_id uuid) RETURNS character varying
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    client_code VARCHAR(10);
    site_code VARCHAR(10);
    random_suffix VARCHAR(10);
    new_token_value VARCHAR(50);
    attempt_count INTEGER := 0;
    max_attempts INTEGER := 100;
BEGIN
    -- Generate fixed-length codes based on UUIDs to ensure consistency
    client_code := UPPER(SUBSTRING(REPLACE(p_client_id::TEXT, '-', ''), 1, 4));
    site_code := UPPER(SUBSTRING(REPLACE(p_site_id::TEXT, '-', ''), 1, 4));
    
    -- Generate unique token
    LOOP
        -- Generate random suffix (6 characters)
        random_suffix := UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 6));
        
        -- Construct token
        new_token_value := 'LANET-' || client_code || '-' || site_code || '-' || random_suffix;
        
        -- Check if token already exists
        IF NOT EXISTS (SELECT 1 FROM agent_installation_tokens WHERE token_value = new_token_value) THEN
            EXIT;
        END IF;
        
        attempt_count := attempt_count + 1;
        IF attempt_count >= max_attempts THEN
            RAISE EXCEPTION 'Unable to generate unique token after % attempts', max_attempts;
        END IF;
    END LOOP;
    
    RETURN new_token_value;
END;
$$;


ALTER FUNCTION public.generate_agent_token(p_client_id uuid, p_site_id uuid) OWNER TO postgres;

--
-- TOC entry 323 (class 1255 OID 34399)
-- Name: generate_ticket_number(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.generate_ticket_number() RETURNS character varying
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN 'TKT-' || LPAD(nextval('ticket_number_seq')::TEXT, 6, '0');
END;
$$;


ALTER FUNCTION public.generate_ticket_number() OWNER TO postgres;

--
-- TOC entry 334 (class 1255 OID 37428)
-- Name: get_current_user_info(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_current_user_info() RETURNS TABLE(user_id uuid, role text, client_id uuid)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.user_id,
        u.role::TEXT,
        u.client_id
    FROM users u
    WHERE u.user_id = current_setting('app.current_user_id', true)::UUID;
END;
$$;


ALTER FUNCTION public.get_current_user_info() OWNER TO postgres;

--
-- TOC entry 333 (class 1255 OID 37114)
-- Name: get_email_routing_recommendation(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_email_routing_recommendation(sender_email text) RETURNS TABLE(site_id uuid, client_id uuid, routing_type text, confidence numeric, explanation text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Step 1: Exact email match in site authorized_emails
    RETURN QUERY
    SELECT 
        s.site_id,
        s.client_id,
        'exact_email_match'::TEXT,
        1.0::DECIMAL,
        'Email found in site authorized emails'::TEXT
    FROM email_routing_sites_view s
    WHERE sender_email = ANY(s.authorized_emails)
    AND s.site_email_routing_enabled = true
    AND s.email_routing_enabled = true
    ORDER BY s.is_primary_site DESC
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Step 2: Email routing rules match
    RETURN QUERY
    SELECT 
        err.site_id,
        err.client_id,
        'routing_rule_match'::TEXT,
        0.9::DECIMAL,
        'Matched email routing rule'::TEXT
    FROM email_routing_rules err
    JOIN email_routing_sites_view s ON err.site_id = s.site_id
    WHERE err.rule_type = 'email' 
    AND err.rule_value = sender_email
    AND err.is_active = true
    AND s.site_email_routing_enabled = true
    AND s.email_routing_enabled = true
    ORDER BY err.priority ASC
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Step 3: Domain match to client's primary site
    RETURN QUERY
    SELECT 
        s.site_id,
        s.client_id,
        'domain_to_primary_site'::TEXT,
        0.8::DECIMAL,
        'Domain matched, routed to primary site'::TEXT
    FROM email_routing_sites_view s
    WHERE SUBSTRING(sender_email FROM '@(.*)') = ANY(
        SELECT SUBSTRING(domain FROM '@(.*)') 
        FROM unnest(s.authorized_domains) AS domain
    )
    AND s.is_primary_site = true
    AND s.site_email_routing_enabled = true
    AND s.email_routing_enabled = true
    LIMIT 1;
    
    -- If found, return
    IF FOUND THEN
        RETURN;
    END IF;
    
    -- Step 4: Fallback to "Unknown Senders" client primary site
    RETURN QUERY
    SELECT 
        s.site_id,
        s.client_id,
        'fallback_unknown'::TEXT,
        0.1::DECIMAL,
        'No match found, routed to fallback client'::TEXT
    FROM email_routing_sites_view s
    WHERE s.client_name = 'Unknown Senders'
    AND s.is_primary_site = true
    LIMIT 1;
    
END;
$$;


ALTER FUNCTION public.get_email_routing_recommendation(sender_email text) OWNER TO postgres;

--
-- TOC entry 324 (class 1255 OID 34400)
-- Name: set_ticket_number(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_ticket_number() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.ticket_number IS NULL THEN
        NEW.ticket_number := generate_ticket_number();
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_ticket_number() OWNER TO postgres;

--
-- TOC entry 330 (class 1255 OID 34487)
-- Name: test_rls_policies(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.test_rls_policies() RETURNS TABLE(test_name text, result boolean, message text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Test 1: Verify RLS is enabled on all tables
    RETURN QUERY
    SELECT
        'RLS Enabled Check'::TEXT,
        (SELECT COUNT(*) = 16 FROM pg_class c
         JOIN pg_namespace n ON c.relnamespace = n.oid
         WHERE n.nspname = 'public'
         AND c.relkind = 'r'
         AND c.relrowsecurity = true),
        'All tables should have RLS enabled'::TEXT;

    -- Test 2: Verify helper functions exist
    RETURN QUERY
    SELECT
        'Helper Functions Check'::TEXT,
        (SELECT COUNT(*) = 4 FROM pg_proc p
         JOIN pg_namespace n ON p.pronamespace = n.oid
         WHERE n.nspname = 'public'
         AND p.proname IN ('current_user_id', 'current_user_role', 'current_user_client_id', 'current_user_site_ids')),
        'All RLS helper functions should exist'::TEXT;

    RETURN;
END;
$$;


ALTER FUNCTION public.test_rls_policies() OWNER TO postgres;

--
-- TOC entry 331 (class 1255 OID 34401)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

--
-- TOC entry 335 (class 1255 OID 37734)
-- Name: validate_agent_token(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.validate_agent_token(p_token_value character varying) RETURNS TABLE(token_id uuid, client_id uuid, site_id uuid, client_name character varying, site_name character varying, is_valid boolean, error_message text)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    token_record RECORD;
BEGIN
    -- Get token record with client and site info
    SELECT 
        t.token_id,
        t.client_id,
        t.site_id,
        t.is_active,
        t.expires_at,
        c.name as client_name,
        s.name as site_name
    INTO token_record
    FROM agent_installation_tokens t
    JOIN clients c ON t.client_id = c.client_id
    JOIN sites s ON t.site_id = s.site_id
    WHERE t.token_value = p_token_value;
    
    -- Check if token exists
    IF NOT FOUND THEN
        RETURN QUERY SELECT 
            NULL::UUID, NULL::UUID, NULL::UUID, 
            NULL::VARCHAR(255), NULL::VARCHAR(255),
            false, 'Token not found'::TEXT;
        RETURN;
    END IF;
    
    -- Check if token is active
    IF NOT token_record.is_active THEN
        RETURN QUERY SELECT 
            token_record.token_id, token_record.client_id, token_record.site_id,
            token_record.client_name, token_record.site_name,
            false, 'Token is inactive'::TEXT;
        RETURN;
    END IF;
    
    -- Check if token is expired
    IF token_record.expires_at IS NOT NULL AND token_record.expires_at < NOW() THEN
        RETURN QUERY SELECT 
            token_record.token_id, token_record.client_id, token_record.site_id,
            token_record.client_name, token_record.site_name,
            false, 'Token has expired'::TEXT;
        RETURN;
    END IF;
    
    -- Token is valid
    RETURN QUERY SELECT 
        token_record.token_id, token_record.client_id, token_record.site_id,
        token_record.client_name, token_record.site_name,
        true, NULL::TEXT;
END;
$$;


ALTER FUNCTION public.validate_agent_token(p_token_value character varying) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 264 (class 1259 OID 37669)
-- Name: agent_installation_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_installation_tokens (
    token_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid NOT NULL,
    site_id uuid NOT NULL,
    token_value character varying(50) NOT NULL,
    is_active boolean DEFAULT true,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp with time zone,
    usage_count integer DEFAULT 0,
    last_used_at timestamp with time zone,
    notes text,
    CONSTRAINT expires_at_future CHECK (((expires_at IS NULL) OR (expires_at > created_at))),
    CONSTRAINT token_value_format CHECK (((token_value)::text ~ '^LANET-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$'::text)),
    CONSTRAINT usage_count_positive CHECK ((usage_count >= 0))
);


ALTER TABLE public.agent_installation_tokens OWNER TO postgres;

--
-- TOC entry 265 (class 1259 OID 37705)
-- Name: agent_token_usage_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_token_usage_history (
    usage_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    token_id uuid NOT NULL,
    used_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    ip_address inet,
    user_agent text,
    computer_name character varying(255),
    hardware_fingerprint jsonb,
    registration_successful boolean DEFAULT false,
    asset_id uuid,
    error_message text
);


ALTER TABLE public.agent_token_usage_history OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 34036)
-- Name: assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assets (
    asset_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid NOT NULL,
    site_id uuid NOT NULL,
    asset_type public.asset_type NOT NULL,
    name character varying(255) NOT NULL,
    serial_number character varying(255),
    purchase_date date,
    warranty_expiry date,
    specifications jsonb,
    license_key character varying(255),
    status character varying(50) DEFAULT 'active'::character varying,
    agent_status public.agent_status DEFAULT 'offline'::public.agent_status,
    last_seen timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    agent_user_id uuid
);


ALTER TABLE public.assets OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 34305)
-- Name: audit_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_log (
    log_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid,
    action character varying(100) NOT NULL,
    table_name character varying(100),
    record_id uuid,
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    user_agent text,
    details text,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.audit_log OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 34642)
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    category_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    parent_id uuid,
    name character varying(100) NOT NULL,
    description text,
    color character varying(7) DEFAULT '#6B7280'::character varying,
    icon character varying(50) DEFAULT 'folder'::character varying,
    is_active boolean DEFAULT true,
    sort_order integer DEFAULT 0,
    auto_assign_to uuid,
    sla_response_hours integer DEFAULT 24,
    sla_resolution_hours integer DEFAULT 72,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT categories_no_self_parent CHECK ((category_id <> parent_id))
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 33959)
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    client_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    rfc character varying(13),
    email character varying(255) NOT NULL,
    phone character varying(20),
    allowed_emails text[],
    address text,
    city character varying(100),
    state character varying(100),
    country character varying(100) DEFAULT 'MÃ©xico'::character varying,
    postal_code character varying(10),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    authorized_domains text[],
    email_routing_enabled boolean DEFAULT true,
    default_priority text DEFAULT 'media'::text,
    CONSTRAINT clients_default_priority_check CHECK ((default_priority = ANY (ARRAY['baja'::text, 'media'::text, 'alta'::text, 'critica'::text]))),
    CONSTRAINT clients_email_check CHECK (((email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text)),
    CONSTRAINT clients_rfc_check CHECK (((rfc)::text ~* '^[A-Z&Ã‘]{3,4}[0-9]{6}[A-Z0-9]{3}$'::text))
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 37391)
-- Name: dashboard_widgets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dashboard_widgets (
    widget_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    widget_type character varying(50) NOT NULL,
    widget_config jsonb NOT NULL,
    position_x integer DEFAULT 0,
    position_y integer DEFAULT 0,
    width integer DEFAULT 1,
    height integer DEFAULT 1,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.dashboard_widgets OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 34671)
-- Name: email_configurations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_configurations (
    config_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    smtp_host character varying(255) NOT NULL,
    smtp_port integer DEFAULT 587 NOT NULL,
    smtp_username character varying(255) NOT NULL,
    smtp_password_encrypted text NOT NULL,
    smtp_use_tls boolean DEFAULT true,
    smtp_use_ssl boolean DEFAULT false,
    imap_host character varying(255),
    imap_port integer DEFAULT 993,
    imap_username character varying(255),
    imap_password_encrypted text,
    imap_use_ssl boolean DEFAULT true,
    imap_folder character varying(100) DEFAULT 'INBOX'::character varying,
    enable_email_to_ticket boolean DEFAULT false,
    default_client_id uuid,
    default_category_id uuid,
    default_priority character varying(20) DEFAULT 'media'::character varying,
    auto_assign_to uuid,
    subject_prefix character varying(50) DEFAULT '[LANET]'::character varying,
    ticket_number_regex character varying(255) DEFAULT '\[LANET-(\d+)\]'::character varying,
    is_active boolean DEFAULT true,
    is_default boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    check_interval_minutes integer DEFAULT 5,
    auto_delete_processed boolean DEFAULT true,
    unknown_sender_client_id uuid,
    smtp_reply_to character varying(255)
);


ALTER TABLE public.email_configurations OWNER TO postgres;

--
-- TOC entry 5860 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN email_configurations.smtp_reply_to; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.email_configurations.smtp_reply_to IS 'Reply-To email address for outgoing notifications. Used when SMTP server is send-only and replies should go to IMAP-enabled address.';


--
-- TOC entry 241 (class 1259 OID 34740)
-- Name: email_processing_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_processing_log (
    log_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    config_id uuid NOT NULL,
    message_id character varying(255) NOT NULL,
    from_email character varying(255) NOT NULL,
    to_email character varying(255) NOT NULL,
    subject text NOT NULL,
    body_text text,
    body_html text,
    processing_status character varying(20) DEFAULT 'pending'::character varying,
    ticket_id uuid,
    action_taken character varying(50),
    error_message text,
    processed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.email_processing_log OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 34710)
-- Name: email_queue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_queue (
    queue_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    config_id uuid NOT NULL,
    to_email character varying(255) NOT NULL,
    cc_emails text[],
    bcc_emails text[],
    subject text NOT NULL,
    body_text text,
    body_html text,
    ticket_id uuid,
    user_id uuid,
    status character varying(20) DEFAULT 'pending'::character varying,
    priority integer DEFAULT 5,
    attempts integer DEFAULT 0,
    max_attempts integer DEFAULT 3,
    next_attempt_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    sent_at timestamp with time zone,
    error_message text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    attachment_data text
);


ALTER TABLE public.email_queue OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 37051)
-- Name: email_routing_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_routing_log (
    log_id uuid DEFAULT gen_random_uuid() NOT NULL,
    email_message_id text NOT NULL,
    sender_email text NOT NULL,
    sender_domain text NOT NULL,
    matched_rule_id uuid,
    routed_client_id uuid,
    routed_site_id uuid,
    routing_decision text NOT NULL,
    routing_confidence numeric(3,2) DEFAULT 0.00,
    created_ticket_id uuid,
    processing_time_ms integer,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.email_routing_log OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 33973)
-- Name: sites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sites (
    site_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    address text NOT NULL,
    city character varying(100) NOT NULL,
    state character varying(100) NOT NULL,
    country character varying(100) DEFAULT 'MÃ©xico'::character varying,
    postal_code character varying(10) NOT NULL,
    latitude numeric(10,8),
    longitude numeric(11,8),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    authorized_emails text[],
    is_primary_site boolean DEFAULT false,
    site_email_routing_enabled boolean DEFAULT true,
    CONSTRAINT sites_latitude_check CHECK (((latitude >= ('-90'::integer)::numeric) AND (latitude <= (90)::numeric))),
    CONSTRAINT sites_longitude_check CHECK (((longitude >= ('-180'::integer)::numeric) AND (longitude <= (180)::numeric))),
    CONSTRAINT sites_postal_code_check CHECK ((length((postal_code)::text) = 5))
);


ALTER TABLE public.sites OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 37089)
-- Name: email_routing_analysis; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.email_routing_analysis AS
 SELECT c.name AS client_name,
    c.authorized_domains,
    s.name AS site_name,
    s.authorized_emails,
    s.is_primary_site,
    count(erl.log_id) AS total_routed_emails,
    count(
        CASE
            WHEN (erl.routing_decision = 'exact_match'::text) THEN 1
            ELSE NULL::integer
        END) AS exact_matches,
    count(
        CASE
            WHEN (erl.routing_decision = 'domain_match'::text) THEN 1
            ELSE NULL::integer
        END) AS domain_matches,
    count(
        CASE
            WHEN (erl.routing_decision = 'fallback'::text) THEN 1
            ELSE NULL::integer
        END) AS fallback_routes,
    count(
        CASE
            WHEN (erl.routing_decision = 'unauthorized'::text) THEN 1
            ELSE NULL::integer
        END) AS unauthorized_emails
   FROM ((public.clients c
     LEFT JOIN public.sites s ON ((c.client_id = s.client_id)))
     LEFT JOIN public.email_routing_log erl ON ((s.site_id = erl.routed_site_id)))
  WHERE ((c.is_active = true) AND ((s.is_active = true) OR (s.is_active IS NULL)))
  GROUP BY c.client_id, c.name, c.authorized_domains, s.site_id, s.name, s.authorized_emails, s.is_primary_site
  ORDER BY c.name, s.name;


ALTER VIEW public.email_routing_analysis OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 37028)
-- Name: email_routing_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_routing_rules (
    rule_id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_id uuid,
    site_id uuid,
    rule_type text NOT NULL,
    rule_value text NOT NULL,
    priority integer DEFAULT 100,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT email_routing_rules_rule_type_check CHECK ((rule_type = ANY (ARRAY['domain'::text, 'email'::text, 'pattern'::text])))
);


ALTER TABLE public.email_routing_rules OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 37109)
-- Name: email_routing_sites_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.email_routing_sites_view AS
 SELECT s.site_id,
    s.client_id,
    s.name AS site_name,
    s.is_primary_site,
    s.site_email_routing_enabled,
    s.authorized_emails,
    c.name AS client_name,
    c.authorized_domains,
    c.email_routing_enabled,
    c.default_priority
   FROM (public.sites s
     JOIN public.clients c ON ((s.client_id = c.client_id)))
  WHERE ((s.is_active = true) AND (c.is_active = true));


ALTER VIEW public.email_routing_sites_view OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 34236)
-- Name: email_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_templates (
    template_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    subject text,
    body text,
    template_type character varying(50) NOT NULL,
    client_id uuid,
    is_default boolean DEFAULT false,
    is_active boolean DEFAULT true,
    variables jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    description text,
    subject_template text,
    body_template text,
    is_html boolean DEFAULT true,
    CONSTRAINT email_templates_type_check CHECK (((template_type)::text = ANY (ARRAY[('ticket_created'::character varying)::text, ('ticket_assigned'::character varying)::text, ('ticket_updated'::character varying)::text, ('ticket_resolved'::character varying)::text, ('ticket_closed'::character varying)::text, ('ticket_commented'::character varying)::text, ('ticket_reopened'::character varying)::text, ('sla_breach'::character varying)::text, ('sla_warning'::character varying)::text, ('auto_response'::character varying)::text])))
);


ALTER TABLE public.email_templates OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 37099)
-- Name: email_templates_view; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.email_templates_view AS
 SELECT template_id,
    name,
    description,
    template_type,
    subject_template,
    body_template,
    is_html,
    is_active,
    is_default,
    variables,
    created_at,
    updated_at,
    client_id,
    created_by
   FROM public.email_templates
  WHERE (is_active = true)
  ORDER BY template_type, name;


ALTER VIEW public.email_templates_view OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 34161)
-- Name: file_attachments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.file_attachments (
    attachment_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ticket_id uuid,
    comment_id uuid,
    filename character varying(255) NOT NULL,
    original_filename character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_size bigint NOT NULL,
    mime_type character varying(100),
    file_hash character varying(64),
    uploaded_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT file_attachments_size_check CHECK ((file_size > 0)),
    CONSTRAINT file_attachments_ticket_or_comment CHECK ((((ticket_id IS NOT NULL) AND (comment_id IS NULL)) OR ((ticket_id IS NULL) AND (comment_id IS NOT NULL))))
);


ALTER TABLE public.file_attachments OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 36994)
-- Name: notification_queue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_queue (
    queue_id uuid DEFAULT gen_random_uuid() NOT NULL,
    ticket_id uuid,
    template_type text NOT NULL,
    recipient_email text NOT NULL,
    recipient_name text,
    subject text NOT NULL,
    body_html text NOT NULL,
    body_plain text NOT NULL,
    status text DEFAULT 'pending'::text,
    attempts integer DEFAULT 0,
    max_attempts integer DEFAULT 3,
    next_retry_at timestamp without time zone,
    sent_at timestamp without time zone,
    error_message text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT notification_queue_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'sent'::text, 'failed'::text, 'retry'::text])))
);


ALTER TABLE public.notification_queue OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 37208)
-- Name: notification_tracking; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_tracking (
    tracking_id uuid DEFAULT gen_random_uuid() NOT NULL,
    ticket_id uuid NOT NULL,
    comment_id uuid,
    notification_type character varying(50) NOT NULL,
    sent_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.notification_tracking OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 34319)
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_reset_tokens (
    token_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    used_at timestamp with time zone,
    CONSTRAINT password_reset_tokens_expiry_check CHECK ((expires_at > created_at))
);


ALTER TABLE public.password_reset_tokens OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 37293)
-- Name: report_configurations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_configurations (
    config_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    template_id uuid NOT NULL,
    client_id uuid,
    report_filters jsonb,
    output_formats text[] DEFAULT ARRAY['pdf'::text],
    is_active boolean DEFAULT true,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.report_configurations OWNER TO postgres;

--
-- TOC entry 5875 (class 0 OID 0)
-- Dependencies: 254
-- Name: TABLE report_configurations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.report_configurations IS 'Configuraciones de reportes creadas por usuarios';


--
-- TOC entry 260 (class 1259 OID 37461)
-- Name: report_configurations_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_configurations_backup (
    config_id uuid,
    name character varying(255),
    description text,
    template_id uuid,
    client_id uuid,
    report_filters jsonb,
    output_formats text[],
    is_active boolean,
    created_by uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.report_configurations_backup OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 37370)
-- Name: report_deliveries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_deliveries (
    delivery_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    execution_id uuid NOT NULL,
    recipient_email character varying(255) NOT NULL,
    delivery_status character varying(20) DEFAULT 'pending'::character varying,
    email_queue_id uuid,
    error_message text,
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT report_deliveries_status_check CHECK (((delivery_status)::text = ANY ((ARRAY['pending'::character varying, 'sent'::character varying, 'failed'::character varying])::text[])))
);


ALTER TABLE public.report_deliveries OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 37476)
-- Name: report_deliveries_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_deliveries_backup (
    delivery_id uuid,
    execution_id uuid,
    recipient_email character varying(255),
    delivery_status character varying(20),
    email_queue_id uuid,
    error_message text,
    sent_at timestamp with time zone,
    created_at timestamp with time zone
);


ALTER TABLE public.report_deliveries_backup OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 37342)
-- Name: report_executions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_executions (
    execution_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    config_id uuid,
    schedule_id uuid,
    execution_type character varying(20) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying,
    output_format character varying(10) NOT NULL,
    file_path text,
    file_size bigint,
    generation_time_ms integer,
    error_message text,
    executed_by uuid,
    started_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp with time zone,
    CONSTRAINT report_executions_format_check CHECK (((output_format)::text = ANY ((ARRAY['pdf'::character varying, 'excel'::character varying, 'csv'::character varying])::text[]))),
    CONSTRAINT report_executions_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'running'::character varying, 'completed'::character varying, 'failed'::character varying])::text[]))),
    CONSTRAINT report_executions_type_check CHECK (((execution_type)::text = ANY ((ARRAY['scheduled'::character varying, 'manual'::character varying])::text[])))
);


ALTER TABLE public.report_executions OWNER TO postgres;

--
-- TOC entry 5880 (class 0 OID 0)
-- Dependencies: 256
-- Name: TABLE report_executions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.report_executions IS 'Historial de ejecuciones de reportes';


--
-- TOC entry 262 (class 1259 OID 37471)
-- Name: report_executions_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_executions_backup (
    execution_id uuid,
    config_id uuid,
    schedule_id uuid,
    execution_type character varying(20),
    status character varying(20),
    output_format character varying(10),
    file_path text,
    file_size bigint,
    generation_time_ms integer,
    error_message text,
    executed_by uuid,
    started_at timestamp with time zone,
    completed_at timestamp with time zone
);


ALTER TABLE public.report_executions_backup OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 37320)
-- Name: report_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_schedules (
    schedule_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    config_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    schedule_type character varying(20) NOT NULL,
    schedule_config jsonb NOT NULL,
    recipients text[] NOT NULL,
    is_active boolean DEFAULT true,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT report_schedules_type_check CHECK (((schedule_type)::text = ANY ((ARRAY['daily'::character varying, 'weekly'::character varying, 'monthly'::character varying, 'custom'::character varying])::text[])))
);


ALTER TABLE public.report_schedules OWNER TO postgres;

--
-- TOC entry 5883 (class 0 OID 0)
-- Dependencies: 255
-- Name: TABLE report_schedules; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.report_schedules IS 'ProgramaciÃ³n automÃ¡tica de reportes';


--
-- TOC entry 261 (class 1259 OID 37466)
-- Name: report_schedules_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_schedules_backup (
    schedule_id uuid,
    config_id uuid,
    name character varying(255),
    schedule_type character varying(20),
    schedule_config jsonb,
    recipients text[],
    is_active boolean,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    created_by uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.report_schedules_backup OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 37275)
-- Name: report_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_templates (
    template_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    report_type character varying(50) NOT NULL,
    template_config jsonb NOT NULL,
    chart_config jsonb,
    is_active boolean DEFAULT true,
    is_system boolean DEFAULT false,
    created_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT report_templates_type_check CHECK (((report_type)::text = ANY ((ARRAY['dashboard'::character varying, 'tickets'::character varying, 'sla'::character varying, 'performance'::character varying, 'custom'::character varying])::text[])))
);


ALTER TABLE public.report_templates OWNER TO postgres;

--
-- TOC entry 5886 (class 0 OID 0)
-- Dependencies: 253
-- Name: TABLE report_templates; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.report_templates IS 'Plantillas de reportes del sistema';


--
-- TOC entry 259 (class 1259 OID 37456)
-- Name: report_templates_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.report_templates_backup (
    template_id uuid,
    name character varying(255),
    description text,
    report_type character varying(50),
    template_config jsonb,
    chart_config jsonb,
    is_active boolean,
    is_system boolean,
    created_by uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


ALTER TABLE public.report_templates_backup OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 34215)
-- Name: sla_compliance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sla_compliance (
    compliance_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ticket_id uuid NOT NULL,
    sla_id uuid NOT NULL,
    response_due_at timestamp with time zone,
    response_time_met boolean,
    response_time_actual integer,
    resolution_due_at timestamp with time zone,
    resolution_time_met boolean,
    resolution_time_actual integer,
    escalated_to_admin boolean DEFAULT false,
    escalation_timestamp timestamp with time zone,
    escalation_reason text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sla_compliance OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 34777)
-- Name: sla_policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sla_policies (
    policy_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    client_id uuid,
    category_id uuid,
    priority character varying(20),
    response_time_hours integer DEFAULT 24 NOT NULL,
    resolution_time_hours integer DEFAULT 72 NOT NULL,
    business_hours_only boolean DEFAULT true,
    business_start_hour integer DEFAULT 8,
    business_end_hour integer DEFAULT 18,
    business_days text[] DEFAULT ARRAY['monday'::text, 'tuesday'::text, 'wednesday'::text, 'thursday'::text, 'friday'::text],
    timezone character varying(50) DEFAULT 'America/Mexico_City'::character varying,
    escalation_enabled boolean DEFAULT true,
    escalation_levels jsonb DEFAULT '[]'::jsonb,
    is_active boolean DEFAULT true,
    is_default boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sla_policies OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 34808)
-- Name: sla_tracking; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sla_tracking (
    tracking_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ticket_id uuid NOT NULL,
    policy_id uuid NOT NULL,
    response_deadline timestamp with time zone,
    resolution_deadline timestamp with time zone,
    first_response_at timestamp with time zone,
    resolved_at timestamp with time zone,
    response_status character varying(20) DEFAULT 'pending'::character varying,
    resolution_status character varying(20) DEFAULT 'pending'::character varying,
    response_breached_at timestamp with time zone,
    resolution_breached_at timestamp with time zone,
    escalation_level integer DEFAULT 0,
    last_escalation_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sla_tracking OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 34187)
-- Name: slas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.slas (
    sla_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    working_days integer[] DEFAULT '{1,2,3,4,5}'::integer[],
    working_hours_start time without time zone DEFAULT '09:00:00'::time without time zone,
    working_hours_end time without time zone DEFAULT '19:00:00'::time without time zone,
    timezone character varying(50) DEFAULT 'America/Mexico_City'::character varying,
    priority_response_time jsonb DEFAULT '{"alta": 120, "baja": 480, "media": 240, "critica": 30}'::jsonb,
    priority_resolution_time jsonb DEFAULT '{"alta": 480, "baja": 2880, "media": 1440, "critica": 240}'::jsonb,
    client_report_recipients text[],
    client_report_frequency character varying(20) DEFAULT 'monthly'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.slas OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 34335)
-- Name: software_licenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.software_licenses (
    license_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid NOT NULL,
    software_name character varying(255) NOT NULL,
    total_licenses integer DEFAULT 1 NOT NULL,
    assigned_licenses integer DEFAULT 0,
    license_key text,
    purchase_date date,
    expiration_date date,
    vendor character varying(255),
    cost numeric(10,2),
    notes text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    CONSTRAINT software_licenses_count_check CHECK ((assigned_licenses <= total_licenses)),
    CONSTRAINT software_licenses_total_check CHECK ((total_licenses > 0))
);


ALTER TABLE public.software_licenses OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 34261)
-- Name: system_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_config (
    config_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    config_key character varying(100) NOT NULL,
    config_value text,
    description text,
    is_encrypted boolean DEFAULT false,
    updated_by uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.system_config OWNER TO postgres;

--
-- TOC entry 5894 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE system_config; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.system_config IS 'System-wide configuration settings for LANET Helpdesk V3';


--
-- TOC entry 232 (class 1259 OID 34278)
-- Name: technician_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.technician_assignments (
    assignment_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    technician_id uuid NOT NULL,
    client_id uuid NOT NULL,
    priority integer DEFAULT 1,
    is_primary boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.technician_assignments OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 34622)
-- Name: ticket_activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_activities (
    activity_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ticket_id uuid NOT NULL,
    user_id uuid NOT NULL,
    action character varying(50) NOT NULL,
    description text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ticket_activities OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 36963)
-- Name: ticket_attachments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_attachments (
    attachment_id uuid DEFAULT gen_random_uuid() NOT NULL,
    ticket_id uuid NOT NULL,
    filename character varying(255) NOT NULL,
    stored_filename character varying(255) NOT NULL,
    file_path text NOT NULL,
    file_size integer NOT NULL,
    content_type character varying(100),
    uploaded_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_active boolean DEFAULT true
);


ALTER TABLE public.ticket_attachments OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 34063)
-- Name: ticket_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_categories (
    category_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid,
    name character varying(255) NOT NULL,
    parent_category_id uuid,
    visibility character varying(20) DEFAULT 'all'::character varying,
    is_active boolean DEFAULT true,
    sort_order integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ticket_categories OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 34139)
-- Name: ticket_comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_comments (
    comment_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ticket_id uuid NOT NULL,
    user_id uuid NOT NULL,
    comment_text text NOT NULL,
    is_internal boolean DEFAULT false,
    is_email_reply boolean DEFAULT false,
    email_message_id character varying(255),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ticket_comments OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 34398)
-- Name: ticket_number_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ticket_number_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ticket_number_seq OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 34887)
-- Name: ticket_resolutions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_resolutions (
    resolution_id uuid DEFAULT gen_random_uuid() NOT NULL,
    ticket_id uuid NOT NULL,
    resolution_notes text NOT NULL,
    resolved_by uuid NOT NULL,
    resolved_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ticket_resolutions OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 34086)
-- Name: tickets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tickets (
    ticket_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ticket_number character varying(20) NOT NULL,
    client_id uuid NOT NULL,
    site_id uuid NOT NULL,
    asset_id uuid,
    created_by uuid NOT NULL,
    assigned_to uuid,
    subject text NOT NULL,
    description text NOT NULL,
    affected_person character varying(255) NOT NULL,
    affected_person_phone character varying(255),
    additional_emails text[],
    priority public.ticket_priority DEFAULT 'media'::public.ticket_priority NOT NULL,
    category_id uuid,
    status public.ticket_status DEFAULT 'nuevo'::public.ticket_status NOT NULL,
    channel public.ticket_channel DEFAULT 'portal'::public.ticket_channel NOT NULL,
    is_email_originated boolean DEFAULT false,
    from_email character varying(255),
    email_message_id character varying(255),
    email_thread_id uuid,
    approval_status character varying(20) DEFAULT 'no_required'::character varying,
    approved_by uuid,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    assigned_at timestamp with time zone,
    resolved_at timestamp with time zone,
    closed_at timestamp with time zone,
    is_active boolean DEFAULT true,
    resolution_notes text,
    notification_email character varying(255),
    affected_person_contact character varying(255) NOT NULL,
    agent_auto_info jsonb,
    CONSTRAINT tickets_email_check CHECK (((from_email IS NULL) OR ((from_email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text))),
    CONSTRAINT tickets_notification_email_check CHECK (((notification_email IS NULL) OR ((notification_email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text)))
);


ALTER TABLE public.tickets OWNER TO postgres;

--
-- TOC entry 5903 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN tickets.affected_person_phone; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.affected_person_phone IS 'Optional phone number of the affected person';


--
-- TOC entry 5904 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN tickets.notification_email; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.notification_email IS 'Optional email address for additional notifications';


--
-- TOC entry 222 (class 1259 OID 34012)
-- Name: user_site_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_site_assignments (
    assignment_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    site_id uuid NOT NULL,
    assigned_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_site_assignments OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 33993)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    client_id uuid,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role public.user_role NOT NULL,
    phone character varying(20),
    is_active boolean DEFAULT true,
    last_login timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    CONSTRAINT users_email_check CHECK (((email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 5417 (class 2606 OID 37682)
-- Name: agent_installation_tokens agent_installation_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_installation_tokens
    ADD CONSTRAINT agent_installation_tokens_pkey PRIMARY KEY (token_id);


--
-- TOC entry 5419 (class 2606 OID 37684)
-- Name: agent_installation_tokens agent_installation_tokens_token_value_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_installation_tokens
    ADD CONSTRAINT agent_installation_tokens_token_value_key UNIQUE (token_value);


--
-- TOC entry 5426 (class 2606 OID 37714)
-- Name: agent_token_usage_history agent_token_usage_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_token_usage_history
    ADD CONSTRAINT agent_token_usage_history_pkey PRIMARY KEY (usage_id);


--
-- TOC entry 5262 (class 2606 OID 34047)
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (asset_id);


--
-- TOC entry 5311 (class 2606 OID 34313)
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (log_id);


--
-- TOC entry 5330 (class 2606 OID 34660)
-- Name: categories categories_name_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_unique UNIQUE (name, parent_id);


--
-- TOC entry 5332 (class 2606 OID 34658)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- TOC entry 5238 (class 2606 OID 33972)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (client_id);


--
-- TOC entry 5413 (class 2606 OID 37405)
-- Name: dashboard_widgets dashboard_widgets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboard_widgets
    ADD CONSTRAINT dashboard_widgets_pkey PRIMARY KEY (widget_id);


--
-- TOC entry 5334 (class 2606 OID 34694)
-- Name: email_configurations email_configurations_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_configurations
    ADD CONSTRAINT email_configurations_name_key UNIQUE (name);


--
-- TOC entry 5336 (class 2606 OID 34692)
-- Name: email_configurations email_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_configurations
    ADD CONSTRAINT email_configurations_pkey PRIMARY KEY (config_id);


--
-- TOC entry 5341 (class 2606 OID 34749)
-- Name: email_processing_log email_processing_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_processing_log
    ADD CONSTRAINT email_processing_log_pkey PRIMARY KEY (log_id);


--
-- TOC entry 5339 (class 2606 OID 34724)
-- Name: email_queue email_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT email_queue_pkey PRIMARY KEY (queue_id);


--
-- TOC entry 5369 (class 2606 OID 37060)
-- Name: email_routing_log email_routing_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_log
    ADD CONSTRAINT email_routing_log_pkey PRIMARY KEY (log_id);


--
-- TOC entry 5362 (class 2606 OID 37040)
-- Name: email_routing_rules email_routing_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_rules
    ADD CONSTRAINT email_routing_rules_pkey PRIMARY KEY (rule_id);


--
-- TOC entry 5296 (class 2606 OID 34250)
-- Name: email_templates email_templates_name_client_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT email_templates_name_client_id_key UNIQUE (name, client_id);


--
-- TOC entry 5298 (class 2606 OID 34248)
-- Name: email_templates email_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT email_templates_pkey PRIMARY KEY (template_id);


--
-- TOC entry 5286 (class 2606 OID 34171)
-- Name: file_attachments file_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_attachments
    ADD CONSTRAINT file_attachments_pkey PRIMARY KEY (attachment_id);


--
-- TOC entry 5360 (class 2606 OID 37007)
-- Name: notification_queue notification_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_queue
    ADD CONSTRAINT notification_queue_pkey PRIMARY KEY (queue_id);


--
-- TOC entry 5378 (class 2606 OID 37215)
-- Name: notification_tracking notification_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_tracking
    ADD CONSTRAINT notification_tracking_pkey PRIMARY KEY (tracking_id);


--
-- TOC entry 5380 (class 2606 OID 37217)
-- Name: notification_tracking notification_tracking_ticket_id_comment_id_notification_typ_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_tracking
    ADD CONSTRAINT notification_tracking_ticket_id_comment_id_notification_typ_key UNIQUE (ticket_id, comment_id, notification_type);


--
-- TOC entry 5319 (class 2606 OID 34327)
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (token_id);


--
-- TOC entry 5321 (class 2606 OID 34329)
-- Name: password_reset_tokens password_reset_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_token_key UNIQUE (token);


--
-- TOC entry 5392 (class 2606 OID 37304)
-- Name: report_configurations report_configurations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_configurations
    ADD CONSTRAINT report_configurations_pkey PRIMARY KEY (config_id);


--
-- TOC entry 5411 (class 2606 OID 37380)
-- Name: report_deliveries report_deliveries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_deliveries
    ADD CONSTRAINT report_deliveries_pkey PRIMARY KEY (delivery_id);


--
-- TOC entry 5407 (class 2606 OID 37354)
-- Name: report_executions report_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_executions
    ADD CONSTRAINT report_executions_pkey PRIMARY KEY (execution_id);


--
-- TOC entry 5400 (class 2606 OID 37331)
-- Name: report_schedules report_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_schedules
    ADD CONSTRAINT report_schedules_pkey PRIMARY KEY (schedule_id);


--
-- TOC entry 5384 (class 2606 OID 37287)
-- Name: report_templates report_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_templates
    ADD CONSTRAINT report_templates_pkey PRIMARY KEY (template_id);


--
-- TOC entry 5246 (class 2606 OID 33987)
-- Name: sites sites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY (site_id);


--
-- TOC entry 5294 (class 2606 OID 34225)
-- Name: sla_compliance sla_compliance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_compliance
    ADD CONSTRAINT sla_compliance_pkey PRIMARY KEY (compliance_id);


--
-- TOC entry 5347 (class 2606 OID 34797)
-- Name: sla_policies sla_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_policies
    ADD CONSTRAINT sla_policies_pkey PRIMARY KEY (policy_id);


--
-- TOC entry 5349 (class 2606 OID 34818)
-- Name: sla_tracking sla_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_pkey PRIMARY KEY (tracking_id);


--
-- TOC entry 5290 (class 2606 OID 34204)
-- Name: slas slas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slas
    ADD CONSTRAINT slas_pkey PRIMARY KEY (sla_id);


--
-- TOC entry 5326 (class 2606 OID 34349)
-- Name: software_licenses software_licenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.software_licenses
    ADD CONSTRAINT software_licenses_pkey PRIMARY KEY (license_id);


--
-- TOC entry 5300 (class 2606 OID 34272)
-- Name: system_config system_config_config_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_config_key_key UNIQUE (config_key);


--
-- TOC entry 5302 (class 2606 OID 34270)
-- Name: system_config system_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_pkey PRIMARY KEY (config_id);


--
-- TOC entry 5307 (class 2606 OID 34287)
-- Name: technician_assignments technician_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.technician_assignments
    ADD CONSTRAINT technician_assignments_pkey PRIMARY KEY (assignment_id);


--
-- TOC entry 5309 (class 2606 OID 34289)
-- Name: technician_assignments technician_assignments_technician_id_client_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.technician_assignments
    ADD CONSTRAINT technician_assignments_technician_id_client_id_key UNIQUE (technician_id, client_id);


--
-- TOC entry 5328 (class 2606 OID 34630)
-- Name: ticket_activities ticket_activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_activities
    ADD CONSTRAINT ticket_activities_pkey PRIMARY KEY (activity_id);


--
-- TOC entry 5355 (class 2606 OID 36972)
-- Name: ticket_attachments ticket_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT ticket_attachments_pkey PRIMARY KEY (attachment_id);


--
-- TOC entry 5268 (class 2606 OID 34075)
-- Name: ticket_categories ticket_categories_name_parent_category_id_client_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_categories
    ADD CONSTRAINT ticket_categories_name_parent_category_id_client_id_key UNIQUE (name, parent_category_id, client_id);


--
-- TOC entry 5270 (class 2606 OID 34073)
-- Name: ticket_categories ticket_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_categories
    ADD CONSTRAINT ticket_categories_pkey PRIMARY KEY (category_id);


--
-- TOC entry 5284 (class 2606 OID 34150)
-- Name: ticket_comments ticket_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_comments
    ADD CONSTRAINT ticket_comments_pkey PRIMARY KEY (comment_id);


--
-- TOC entry 5353 (class 2606 OID 34896)
-- Name: ticket_resolutions ticket_resolutions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_resolutions
    ADD CONSTRAINT ticket_resolutions_pkey PRIMARY KEY (resolution_id);


--
-- TOC entry 5279 (class 2606 OID 34101)
-- Name: tickets tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pkey PRIMARY KEY (ticket_id);


--
-- TOC entry 5281 (class 2606 OID 34103)
-- Name: tickets tickets_ticket_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_ticket_number_key UNIQUE (ticket_number);


--
-- TOC entry 5258 (class 2606 OID 34018)
-- Name: user_site_assignments user_site_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_site_assignments
    ADD CONSTRAINT user_site_assignments_pkey PRIMARY KEY (assignment_id);


--
-- TOC entry 5260 (class 2606 OID 34020)
-- Name: user_site_assignments user_site_assignments_user_id_site_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_site_assignments
    ADD CONSTRAINT user_site_assignments_user_id_site_id_key UNIQUE (user_id, site_id);


--
-- TOC entry 5252 (class 2606 OID 34006)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5254 (class 2606 OID 34004)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 5420 (class 1259 OID 37702)
-- Name: idx_agent_tokens_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_tokens_active ON public.agent_installation_tokens USING btree (is_active) WHERE (is_active = true);


--
-- TOC entry 5421 (class 1259 OID 37700)
-- Name: idx_agent_tokens_client_site; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_tokens_client_site ON public.agent_installation_tokens USING btree (client_id, site_id);


--
-- TOC entry 5422 (class 1259 OID 37703)
-- Name: idx_agent_tokens_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_tokens_created_by ON public.agent_installation_tokens USING btree (created_by);


--
-- TOC entry 5423 (class 1259 OID 37704)
-- Name: idx_agent_tokens_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_tokens_expires_at ON public.agent_installation_tokens USING btree (expires_at) WHERE (expires_at IS NOT NULL);


--
-- TOC entry 5424 (class 1259 OID 37701)
-- Name: idx_agent_tokens_token_value; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_tokens_token_value ON public.agent_installation_tokens USING btree (token_value);


--
-- TOC entry 5263 (class 1259 OID 34373)
-- Name: idx_assets_agent_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assets_agent_status ON public.assets USING btree (agent_status);


--
-- TOC entry 5264 (class 1259 OID 34370)
-- Name: idx_assets_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assets_client_id ON public.assets USING btree (client_id);


--
-- TOC entry 5265 (class 1259 OID 34371)
-- Name: idx_assets_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assets_site_id ON public.assets USING btree (site_id);


--
-- TOC entry 5266 (class 1259 OID 34372)
-- Name: idx_assets_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assets_status ON public.assets USING btree (status);


--
-- TOC entry 5312 (class 1259 OID 34391)
-- Name: idx_audit_log_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_action ON public.audit_log USING btree (action);


--
-- TOC entry 5313 (class 1259 OID 34390)
-- Name: idx_audit_log_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_timestamp ON public.audit_log USING btree ("timestamp");


--
-- TOC entry 5314 (class 1259 OID 34389)
-- Name: idx_audit_log_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_user_id ON public.audit_log USING btree (user_id);


--
-- TOC entry 5239 (class 1259 OID 34360)
-- Name: idx_clients_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clients_active ON public.clients USING btree (is_active);


--
-- TOC entry 5240 (class 1259 OID 34361)
-- Name: idx_clients_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clients_name ON public.clients USING btree (name);


--
-- TOC entry 5414 (class 1259 OID 37426)
-- Name: idx_dashboard_widgets_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dashboard_widgets_active ON public.dashboard_widgets USING btree (is_active);


--
-- TOC entry 5415 (class 1259 OID 37425)
-- Name: idx_dashboard_widgets_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dashboard_widgets_user ON public.dashboard_widgets USING btree (user_id);


--
-- TOC entry 5337 (class 1259 OID 37145)
-- Name: idx_email_configurations_reply_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_configurations_reply_to ON public.email_configurations USING btree (smtp_reply_to) WHERE (smtp_reply_to IS NOT NULL);


--
-- TOC entry 5342 (class 1259 OID 37020)
-- Name: idx_email_processing_log_message_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_processing_log_message_id ON public.email_processing_log USING btree (message_id);


--
-- TOC entry 5343 (class 1259 OID 37013)
-- Name: idx_email_processing_log_processed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_processing_log_processed_at ON public.email_processing_log USING btree (processed_at);


--
-- TOC entry 5344 (class 1259 OID 37021)
-- Name: idx_email_processing_log_sender; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_processing_log_sender ON public.email_processing_log USING btree (from_email);


--
-- TOC entry 5345 (class 1259 OID 37022)
-- Name: idx_email_processing_log_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_processing_log_status ON public.email_processing_log USING btree (processing_status);


--
-- TOC entry 5370 (class 1259 OID 37087)
-- Name: idx_email_routing_log_decision; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_log_decision ON public.email_routing_log USING btree (routing_decision);


--
-- TOC entry 5371 (class 1259 OID 37086)
-- Name: idx_email_routing_log_sender_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_log_sender_domain ON public.email_routing_log USING btree (sender_domain);


--
-- TOC entry 5372 (class 1259 OID 37085)
-- Name: idx_email_routing_log_sender_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_log_sender_email ON public.email_routing_log USING btree (sender_email);


--
-- TOC entry 5363 (class 1259 OID 37084)
-- Name: idx_email_routing_rules_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_rules_active ON public.email_routing_rules USING btree (is_active);


--
-- TOC entry 5364 (class 1259 OID 37081)
-- Name: idx_email_routing_rules_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_rules_client_id ON public.email_routing_rules USING btree (client_id);


--
-- TOC entry 5365 (class 1259 OID 37108)
-- Name: idx_email_routing_rules_lookup; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_rules_lookup ON public.email_routing_rules USING btree (rule_type, rule_value, is_active);


--
-- TOC entry 5366 (class 1259 OID 37082)
-- Name: idx_email_routing_rules_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_rules_site_id ON public.email_routing_rules USING btree (site_id);


--
-- TOC entry 5367 (class 1259 OID 37083)
-- Name: idx_email_routing_rules_type_value; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_email_routing_rules_type_value ON public.email_routing_rules USING btree (rule_type, rule_value);


--
-- TOC entry 5356 (class 1259 OID 37015)
-- Name: idx_notification_queue_next_retry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_queue_next_retry ON public.notification_queue USING btree (next_retry_at);


--
-- TOC entry 5357 (class 1259 OID 37014)
-- Name: idx_notification_queue_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_queue_status ON public.notification_queue USING btree (status);


--
-- TOC entry 5358 (class 1259 OID 37016)
-- Name: idx_notification_queue_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_queue_ticket_id ON public.notification_queue USING btree (ticket_id);


--
-- TOC entry 5373 (class 1259 OID 37229)
-- Name: idx_notification_tracking_comment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_tracking_comment_id ON public.notification_tracking USING btree (comment_id);


--
-- TOC entry 5374 (class 1259 OID 37231)
-- Name: idx_notification_tracking_sent_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_tracking_sent_at ON public.notification_tracking USING btree (sent_at);


--
-- TOC entry 5375 (class 1259 OID 37228)
-- Name: idx_notification_tracking_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_tracking_ticket_id ON public.notification_tracking USING btree (ticket_id);


--
-- TOC entry 5376 (class 1259 OID 37230)
-- Name: idx_notification_tracking_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_tracking_type ON public.notification_tracking USING btree (notification_type);


--
-- TOC entry 5315 (class 1259 OID 34394)
-- Name: idx_password_reset_tokens_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_password_reset_tokens_expires_at ON public.password_reset_tokens USING btree (expires_at);


--
-- TOC entry 5316 (class 1259 OID 34393)
-- Name: idx_password_reset_tokens_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_password_reset_tokens_token ON public.password_reset_tokens USING btree (token);


--
-- TOC entry 5317 (class 1259 OID 34392)
-- Name: idx_password_reset_tokens_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_password_reset_tokens_user_id ON public.password_reset_tokens USING btree (user_id);


--
-- TOC entry 5385 (class 1259 OID 37415)
-- Name: idx_report_configurations_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_configurations_active ON public.report_configurations USING btree (is_active);


--
-- TOC entry 5386 (class 1259 OID 37414)
-- Name: idx_report_configurations_client; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_configurations_client ON public.report_configurations USING btree (client_id);


--
-- TOC entry 5387 (class 1259 OID 37444)
-- Name: idx_report_configurations_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_configurations_client_id ON public.report_configurations USING btree (client_id);


--
-- TOC entry 5388 (class 1259 OID 37446)
-- Name: idx_report_configurations_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_configurations_created_by ON public.report_configurations USING btree (created_by);


--
-- TOC entry 5389 (class 1259 OID 37413)
-- Name: idx_report_configurations_template; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_configurations_template ON public.report_configurations USING btree (template_id);


--
-- TOC entry 5390 (class 1259 OID 37445)
-- Name: idx_report_configurations_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_configurations_template_id ON public.report_configurations USING btree (template_id);


--
-- TOC entry 5408 (class 1259 OID 37423)
-- Name: idx_report_deliveries_execution; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_deliveries_execution ON public.report_deliveries USING btree (execution_id);


--
-- TOC entry 5409 (class 1259 OID 37424)
-- Name: idx_report_deliveries_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_deliveries_status ON public.report_deliveries USING btree (delivery_status);


--
-- TOC entry 5401 (class 1259 OID 37419)
-- Name: idx_report_executions_config; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_executions_config ON public.report_executions USING btree (config_id);


--
-- TOC entry 5402 (class 1259 OID 37447)
-- Name: idx_report_executions_config_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_executions_config_id ON public.report_executions USING btree (config_id);


--
-- TOC entry 5403 (class 1259 OID 37420)
-- Name: idx_report_executions_schedule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_executions_schedule ON public.report_executions USING btree (schedule_id);


--
-- TOC entry 5404 (class 1259 OID 37422)
-- Name: idx_report_executions_started; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_executions_started ON public.report_executions USING btree (started_at);


--
-- TOC entry 5405 (class 1259 OID 37421)
-- Name: idx_report_executions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_executions_status ON public.report_executions USING btree (status);


--
-- TOC entry 5393 (class 1259 OID 37418)
-- Name: idx_report_schedules_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_active ON public.report_schedules USING btree (is_active);


--
-- TOC entry 5394 (class 1259 OID 37416)
-- Name: idx_report_schedules_config; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_config ON public.report_schedules USING btree (config_id);


--
-- TOC entry 5395 (class 1259 OID 37448)
-- Name: idx_report_schedules_config_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_config_id ON public.report_schedules USING btree (config_id);


--
-- TOC entry 5396 (class 1259 OID 37450)
-- Name: idx_report_schedules_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_is_active ON public.report_schedules USING btree (is_active);


--
-- TOC entry 5397 (class 1259 OID 37417)
-- Name: idx_report_schedules_next_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_next_run ON public.report_schedules USING btree (next_run_at);


--
-- TOC entry 5398 (class 1259 OID 37449)
-- Name: idx_report_schedules_next_run_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_schedules_next_run_at ON public.report_schedules USING btree (next_run_at);


--
-- TOC entry 5381 (class 1259 OID 37412)
-- Name: idx_report_templates_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_templates_active ON public.report_templates USING btree (is_active);


--
-- TOC entry 5382 (class 1259 OID 37411)
-- Name: idx_report_templates_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_templates_type ON public.report_templates USING btree (report_type);


--
-- TOC entry 5241 (class 1259 OID 34363)
-- Name: idx_sites_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sites_active ON public.sites USING btree (is_active);


--
-- TOC entry 5242 (class 1259 OID 37106)
-- Name: idx_sites_authorized_emails; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sites_authorized_emails ON public.sites USING gin (authorized_emails);


--
-- TOC entry 5243 (class 1259 OID 34362)
-- Name: idx_sites_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sites_client_id ON public.sites USING btree (client_id);


--
-- TOC entry 5244 (class 1259 OID 37107)
-- Name: idx_sites_primary_routing; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sites_primary_routing ON public.sites USING btree (client_id, is_primary_site, site_email_routing_enabled);


--
-- TOC entry 5291 (class 1259 OID 34385)
-- Name: idx_sla_compliance_escalated; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sla_compliance_escalated ON public.sla_compliance USING btree (escalated_to_admin);


--
-- TOC entry 5292 (class 1259 OID 34384)
-- Name: idx_sla_compliance_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sla_compliance_ticket_id ON public.sla_compliance USING btree (ticket_id);


--
-- TOC entry 5287 (class 1259 OID 34383)
-- Name: idx_slas_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_slas_active ON public.slas USING btree (is_active);


--
-- TOC entry 5288 (class 1259 OID 34382)
-- Name: idx_slas_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_slas_client_id ON public.slas USING btree (client_id);


--
-- TOC entry 5322 (class 1259 OID 34397)
-- Name: idx_software_licenses_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_software_licenses_active ON public.software_licenses USING btree (is_active);


--
-- TOC entry 5323 (class 1259 OID 34395)
-- Name: idx_software_licenses_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_software_licenses_client_id ON public.software_licenses USING btree (client_id);


--
-- TOC entry 5324 (class 1259 OID 34396)
-- Name: idx_software_licenses_expiration_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_software_licenses_expiration_date ON public.software_licenses USING btree (expiration_date);


--
-- TOC entry 5303 (class 1259 OID 34388)
-- Name: idx_technician_assignments_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_technician_assignments_active ON public.technician_assignments USING btree (is_active);


--
-- TOC entry 5304 (class 1259 OID 34387)
-- Name: idx_technician_assignments_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_technician_assignments_client_id ON public.technician_assignments USING btree (client_id);


--
-- TOC entry 5305 (class 1259 OID 34386)
-- Name: idx_technician_assignments_technician_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_technician_assignments_technician_id ON public.technician_assignments USING btree (technician_id);


--
-- TOC entry 5282 (class 1259 OID 34381)
-- Name: idx_ticket_comments_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ticket_comments_ticket_id ON public.ticket_comments USING btree (ticket_id);


--
-- TOC entry 5350 (class 1259 OID 34908)
-- Name: idx_ticket_resolutions_resolved_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ticket_resolutions_resolved_at ON public.ticket_resolutions USING btree (resolved_at);


--
-- TOC entry 5351 (class 1259 OID 34907)
-- Name: idx_ticket_resolutions_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ticket_resolutions_ticket_id ON public.ticket_resolutions USING btree (ticket_id);


--
-- TOC entry 5271 (class 1259 OID 34376)
-- Name: idx_tickets_assigned_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_assigned_to ON public.tickets USING btree (assigned_to);


--
-- TOC entry 5272 (class 1259 OID 34374)
-- Name: idx_tickets_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_client_id ON public.tickets USING btree (client_id);


--
-- TOC entry 5273 (class 1259 OID 34379)
-- Name: idx_tickets_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_created_at ON public.tickets USING btree (created_at);


--
-- TOC entry 5274 (class 1259 OID 34380)
-- Name: idx_tickets_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_number ON public.tickets USING btree (ticket_number);


--
-- TOC entry 5275 (class 1259 OID 34378)
-- Name: idx_tickets_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_priority ON public.tickets USING btree (priority);


--
-- TOC entry 5276 (class 1259 OID 34375)
-- Name: idx_tickets_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_site_id ON public.tickets USING btree (site_id);


--
-- TOC entry 5277 (class 1259 OID 34377)
-- Name: idx_tickets_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_status ON public.tickets USING btree (status);


--
-- TOC entry 5427 (class 1259 OID 37725)
-- Name: idx_token_usage_token_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_token_usage_token_id ON public.agent_token_usage_history USING btree (token_id);


--
-- TOC entry 5428 (class 1259 OID 37726)
-- Name: idx_token_usage_used_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_token_usage_used_at ON public.agent_token_usage_history USING btree (used_at);


--
-- TOC entry 5255 (class 1259 OID 34369)
-- Name: idx_user_site_assignments_site_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_site_assignments_site_id ON public.user_site_assignments USING btree (site_id);


--
-- TOC entry 5256 (class 1259 OID 34368)
-- Name: idx_user_site_assignments_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_site_assignments_user_id ON public.user_site_assignments USING btree (user_id);


--
-- TOC entry 5247 (class 1259 OID 34367)
-- Name: idx_users_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_active ON public.users USING btree (is_active);


--
-- TOC entry 5248 (class 1259 OID 34364)
-- Name: idx_users_client_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_client_id ON public.users USING btree (client_id);


--
-- TOC entry 5249 (class 1259 OID 34366)
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- TOC entry 5250 (class 1259 OID 34365)
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_role ON public.users USING btree (role);


--
-- TOC entry 5513 (class 2620 OID 34413)
-- Name: clients audit_clients_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER audit_clients_trigger AFTER INSERT OR DELETE OR UPDATE ON public.clients FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_function();


--
-- TOC entry 5520 (class 2620 OID 34415)
-- Name: tickets audit_tickets_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER audit_tickets_trigger AFTER INSERT OR DELETE OR UPDATE ON public.tickets FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_function();


--
-- TOC entry 5517 (class 2620 OID 34414)
-- Name: users audit_users_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER audit_users_trigger AFTER INSERT OR DELETE OR UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_function();


--
-- TOC entry 5521 (class 2620 OID 34403)
-- Name: tickets set_ticket_number_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER set_ticket_number_trigger BEFORE INSERT ON public.tickets FOR EACH ROW EXECUTE FUNCTION public.set_ticket_number();


--
-- TOC entry 5515 (class 2620 OID 37105)
-- Name: sites trigger_ensure_single_primary_site; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_ensure_single_primary_site BEFORE INSERT OR UPDATE ON public.sites FOR EACH ROW EXECUTE FUNCTION public.ensure_single_primary_site();


--
-- TOC entry 5519 (class 2620 OID 34407)
-- Name: assets update_assets_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON public.assets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5514 (class 2620 OID 34404)
-- Name: clients update_clients_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON public.clients FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5528 (class 2620 OID 37017)
-- Name: email_processing_log update_email_processing_log_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_email_processing_log_updated_at BEFORE UPDATE ON public.email_processing_log FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5530 (class 2620 OID 37088)
-- Name: email_routing_rules update_email_routing_rules_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_email_routing_rules_updated_at BEFORE UPDATE ON public.email_routing_rules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5526 (class 2620 OID 37018)
-- Name: email_templates update_email_templates_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_email_templates_updated_at BEFORE UPDATE ON public.email_templates FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5529 (class 2620 OID 37019)
-- Name: notification_queue update_notification_queue_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_notification_queue_updated_at BEFORE UPDATE ON public.notification_queue FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5531 (class 2620 OID 37451)
-- Name: report_configurations update_report_configurations_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_report_configurations_updated_at BEFORE UPDATE ON public.report_configurations FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5532 (class 2620 OID 37452)
-- Name: report_schedules update_report_schedules_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_report_schedules_updated_at BEFORE UPDATE ON public.report_schedules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5516 (class 2620 OID 34405)
-- Name: sites update_sites_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_sites_updated_at BEFORE UPDATE ON public.sites FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5525 (class 2620 OID 34411)
-- Name: sla_compliance update_sla_compliance_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_sla_compliance_updated_at BEFORE UPDATE ON public.sla_compliance FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5524 (class 2620 OID 34410)
-- Name: slas update_slas_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_slas_updated_at BEFORE UPDATE ON public.slas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5527 (class 2620 OID 34412)
-- Name: software_licenses update_software_licenses_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_software_licenses_updated_at BEFORE UPDATE ON public.software_licenses FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5523 (class 2620 OID 34409)
-- Name: ticket_comments update_ticket_comments_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_ticket_comments_updated_at BEFORE UPDATE ON public.ticket_comments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5522 (class 2620 OID 34408)
-- Name: tickets update_tickets_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON public.tickets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5518 (class 2620 OID 34406)
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5508 (class 2606 OID 37685)
-- Name: agent_installation_tokens agent_installation_tokens_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_installation_tokens
    ADD CONSTRAINT agent_installation_tokens_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5509 (class 2606 OID 37695)
-- Name: agent_installation_tokens agent_installation_tokens_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_installation_tokens
    ADD CONSTRAINT agent_installation_tokens_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5510 (class 2606 OID 37690)
-- Name: agent_installation_tokens agent_installation_tokens_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_installation_tokens
    ADD CONSTRAINT agent_installation_tokens_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- TOC entry 5511 (class 2606 OID 37720)
-- Name: agent_token_usage_history agent_token_usage_history_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_token_usage_history
    ADD CONSTRAINT agent_token_usage_history_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(asset_id);


--
-- TOC entry 5512 (class 2606 OID 37715)
-- Name: agent_token_usage_history agent_token_usage_history_token_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_token_usage_history
    ADD CONSTRAINT agent_token_usage_history_token_id_fkey FOREIGN KEY (token_id) REFERENCES public.agent_installation_tokens(token_id) ON DELETE CASCADE;


--
-- TOC entry 5434 (class 2606 OID 37869)
-- Name: assets assets_agent_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_agent_user_id_fkey FOREIGN KEY (agent_user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5435 (class 2606 OID 34048)
-- Name: assets assets_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5436 (class 2606 OID 34058)
-- Name: assets assets_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5437 (class 2606 OID 34053)
-- Name: assets assets_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- TOC entry 5462 (class 2606 OID 34314)
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5468 (class 2606 OID 34666)
-- Name: categories categories_auto_assign_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_auto_assign_to_fkey FOREIGN KEY (auto_assign_to) REFERENCES public.users(user_id);


--
-- TOC entry 5469 (class 2606 OID 34661)
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.categories(category_id) ON DELETE CASCADE;


--
-- TOC entry 5507 (class 2606 OID 37406)
-- Name: dashboard_widgets dashboard_widgets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboard_widgets
    ADD CONSTRAINT dashboard_widgets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5470 (class 2606 OID 34705)
-- Name: email_configurations email_configurations_auto_assign_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_configurations
    ADD CONSTRAINT email_configurations_auto_assign_to_fkey FOREIGN KEY (auto_assign_to) REFERENCES public.users(user_id);


--
-- TOC entry 5471 (class 2606 OID 34700)
-- Name: email_configurations email_configurations_default_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_configurations
    ADD CONSTRAINT email_configurations_default_category_id_fkey FOREIGN KEY (default_category_id) REFERENCES public.categories(category_id);


--
-- TOC entry 5472 (class 2606 OID 34695)
-- Name: email_configurations email_configurations_default_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_configurations
    ADD CONSTRAINT email_configurations_default_client_id_fkey FOREIGN KEY (default_client_id) REFERENCES public.clients(client_id);


--
-- TOC entry 5473 (class 2606 OID 36989)
-- Name: email_configurations email_configurations_unknown_sender_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_configurations
    ADD CONSTRAINT email_configurations_unknown_sender_client_id_fkey FOREIGN KEY (unknown_sender_client_id) REFERENCES public.clients(client_id);


--
-- TOC entry 5477 (class 2606 OID 34750)
-- Name: email_processing_log email_processing_log_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_processing_log
    ADD CONSTRAINT email_processing_log_config_id_fkey FOREIGN KEY (config_id) REFERENCES public.email_configurations(config_id);


--
-- TOC entry 5478 (class 2606 OID 34755)
-- Name: email_processing_log email_processing_log_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_processing_log
    ADD CONSTRAINT email_processing_log_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id);


--
-- TOC entry 5474 (class 2606 OID 34725)
-- Name: email_queue email_queue_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT email_queue_config_id_fkey FOREIGN KEY (config_id) REFERENCES public.email_configurations(config_id);


--
-- TOC entry 5475 (class 2606 OID 34730)
-- Name: email_queue email_queue_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT email_queue_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id);


--
-- TOC entry 5476 (class 2606 OID 34735)
-- Name: email_queue email_queue_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_queue
    ADD CONSTRAINT email_queue_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5490 (class 2606 OID 37076)
-- Name: email_routing_log email_routing_log_created_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_log
    ADD CONSTRAINT email_routing_log_created_ticket_id_fkey FOREIGN KEY (created_ticket_id) REFERENCES public.tickets(ticket_id);


--
-- TOC entry 5491 (class 2606 OID 37061)
-- Name: email_routing_log email_routing_log_matched_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_log
    ADD CONSTRAINT email_routing_log_matched_rule_id_fkey FOREIGN KEY (matched_rule_id) REFERENCES public.email_routing_rules(rule_id);


--
-- TOC entry 5492 (class 2606 OID 37066)
-- Name: email_routing_log email_routing_log_routed_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_log
    ADD CONSTRAINT email_routing_log_routed_client_id_fkey FOREIGN KEY (routed_client_id) REFERENCES public.clients(client_id);


--
-- TOC entry 5493 (class 2606 OID 37071)
-- Name: email_routing_log email_routing_log_routed_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_log
    ADD CONSTRAINT email_routing_log_routed_site_id_fkey FOREIGN KEY (routed_site_id) REFERENCES public.sites(site_id);


--
-- TOC entry 5488 (class 2606 OID 37041)
-- Name: email_routing_rules email_routing_rules_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_rules
    ADD CONSTRAINT email_routing_rules_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5489 (class 2606 OID 37046)
-- Name: email_routing_rules email_routing_rules_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_routing_rules
    ADD CONSTRAINT email_routing_rules_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- TOC entry 5456 (class 2606 OID 34251)
-- Name: email_templates email_templates_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT email_templates_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id);


--
-- TOC entry 5457 (class 2606 OID 34256)
-- Name: email_templates email_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_templates
    ADD CONSTRAINT email_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5449 (class 2606 OID 34177)
-- Name: file_attachments file_attachments_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_attachments
    ADD CONSTRAINT file_attachments_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.ticket_comments(comment_id) ON DELETE CASCADE;


--
-- TOC entry 5450 (class 2606 OID 34172)
-- Name: file_attachments file_attachments_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_attachments
    ADD CONSTRAINT file_attachments_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id) ON DELETE CASCADE;


--
-- TOC entry 5451 (class 2606 OID 34182)
-- Name: file_attachments file_attachments_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_attachments
    ADD CONSTRAINT file_attachments_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(user_id);


--
-- TOC entry 5487 (class 2606 OID 37008)
-- Name: notification_queue notification_queue_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_queue
    ADD CONSTRAINT notification_queue_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id);


--
-- TOC entry 5494 (class 2606 OID 37223)
-- Name: notification_tracking notification_tracking_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_tracking
    ADD CONSTRAINT notification_tracking_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.ticket_comments(comment_id);


--
-- TOC entry 5495 (class 2606 OID 37218)
-- Name: notification_tracking notification_tracking_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_tracking
    ADD CONSTRAINT notification_tracking_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id);


--
-- TOC entry 5463 (class 2606 OID 34330)
-- Name: password_reset_tokens password_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 5497 (class 2606 OID 37310)
-- Name: report_configurations report_configurations_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_configurations
    ADD CONSTRAINT report_configurations_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id);


--
-- TOC entry 5498 (class 2606 OID 37315)
-- Name: report_configurations report_configurations_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_configurations
    ADD CONSTRAINT report_configurations_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5499 (class 2606 OID 37305)
-- Name: report_configurations report_configurations_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_configurations
    ADD CONSTRAINT report_configurations_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.report_templates(template_id);


--
-- TOC entry 5505 (class 2606 OID 37386)
-- Name: report_deliveries report_deliveries_email_queue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_deliveries
    ADD CONSTRAINT report_deliveries_email_queue_id_fkey FOREIGN KEY (email_queue_id) REFERENCES public.email_queue(queue_id);


--
-- TOC entry 5506 (class 2606 OID 37381)
-- Name: report_deliveries report_deliveries_execution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_deliveries
    ADD CONSTRAINT report_deliveries_execution_id_fkey FOREIGN KEY (execution_id) REFERENCES public.report_executions(execution_id);


--
-- TOC entry 5502 (class 2606 OID 37355)
-- Name: report_executions report_executions_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_executions
    ADD CONSTRAINT report_executions_config_id_fkey FOREIGN KEY (config_id) REFERENCES public.report_configurations(config_id);


--
-- TOC entry 5503 (class 2606 OID 37365)
-- Name: report_executions report_executions_executed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_executions
    ADD CONSTRAINT report_executions_executed_by_fkey FOREIGN KEY (executed_by) REFERENCES public.users(user_id);


--
-- TOC entry 5504 (class 2606 OID 37360)
-- Name: report_executions report_executions_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_executions
    ADD CONSTRAINT report_executions_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.report_schedules(schedule_id);


--
-- TOC entry 5500 (class 2606 OID 37332)
-- Name: report_schedules report_schedules_config_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_schedules
    ADD CONSTRAINT report_schedules_config_id_fkey FOREIGN KEY (config_id) REFERENCES public.report_configurations(config_id);


--
-- TOC entry 5501 (class 2606 OID 37337)
-- Name: report_schedules report_schedules_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_schedules
    ADD CONSTRAINT report_schedules_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5496 (class 2606 OID 37288)
-- Name: report_templates report_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.report_templates
    ADD CONSTRAINT report_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5429 (class 2606 OID 33988)
-- Name: sites sites_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5454 (class 2606 OID 34231)
-- Name: sla_compliance sla_compliance_sla_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_compliance
    ADD CONSTRAINT sla_compliance_sla_id_fkey FOREIGN KEY (sla_id) REFERENCES public.slas(sla_id);


--
-- TOC entry 5455 (class 2606 OID 34226)
-- Name: sla_compliance sla_compliance_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_compliance
    ADD CONSTRAINT sla_compliance_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id) ON DELETE CASCADE;


--
-- TOC entry 5479 (class 2606 OID 34803)
-- Name: sla_policies sla_policies_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_policies
    ADD CONSTRAINT sla_policies_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id);


--
-- TOC entry 5480 (class 2606 OID 34798)
-- Name: sla_policies sla_policies_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_policies
    ADD CONSTRAINT sla_policies_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id);


--
-- TOC entry 5481 (class 2606 OID 34824)
-- Name: sla_tracking sla_tracking_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.sla_policies(policy_id);


--
-- TOC entry 5482 (class 2606 OID 34819)
-- Name: sla_tracking sla_tracking_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id) ON DELETE CASCADE;


--
-- TOC entry 5452 (class 2606 OID 34205)
-- Name: slas slas_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slas
    ADD CONSTRAINT slas_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5453 (class 2606 OID 34210)
-- Name: slas slas_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.slas
    ADD CONSTRAINT slas_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5464 (class 2606 OID 34350)
-- Name: software_licenses software_licenses_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.software_licenses
    ADD CONSTRAINT software_licenses_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5465 (class 2606 OID 34355)
-- Name: software_licenses software_licenses_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.software_licenses
    ADD CONSTRAINT software_licenses_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5458 (class 2606 OID 34273)
-- Name: system_config system_config_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(user_id);


--
-- TOC entry 5459 (class 2606 OID 34295)
-- Name: technician_assignments technician_assignments_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.technician_assignments
    ADD CONSTRAINT technician_assignments_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5460 (class 2606 OID 34300)
-- Name: technician_assignments technician_assignments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.technician_assignments
    ADD CONSTRAINT technician_assignments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5461 (class 2606 OID 34290)
-- Name: technician_assignments technician_assignments_technician_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.technician_assignments
    ADD CONSTRAINT technician_assignments_technician_id_fkey FOREIGN KEY (technician_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 5466 (class 2606 OID 34631)
-- Name: ticket_activities ticket_activities_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_activities
    ADD CONSTRAINT ticket_activities_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id) ON DELETE CASCADE;


--
-- TOC entry 5467 (class 2606 OID 34636)
-- Name: ticket_activities ticket_activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_activities
    ADD CONSTRAINT ticket_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5485 (class 2606 OID 36973)
-- Name: ticket_attachments ticket_attachments_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT ticket_attachments_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id) ON DELETE CASCADE;


--
-- TOC entry 5486 (class 2606 OID 36978)
-- Name: ticket_attachments ticket_attachments_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT ticket_attachments_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(user_id);


--
-- TOC entry 5438 (class 2606 OID 34076)
-- Name: ticket_categories ticket_categories_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_categories
    ADD CONSTRAINT ticket_categories_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5439 (class 2606 OID 34081)
-- Name: ticket_categories ticket_categories_parent_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_categories
    ADD CONSTRAINT ticket_categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES public.ticket_categories(category_id);


--
-- TOC entry 5447 (class 2606 OID 34151)
-- Name: ticket_comments ticket_comments_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_comments
    ADD CONSTRAINT ticket_comments_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id) ON DELETE CASCADE;


--
-- TOC entry 5448 (class 2606 OID 34156)
-- Name: ticket_comments ticket_comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_comments
    ADD CONSTRAINT ticket_comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5483 (class 2606 OID 34902)
-- Name: ticket_resolutions ticket_resolutions_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_resolutions
    ADD CONSTRAINT ticket_resolutions_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(user_id);


--
-- TOC entry 5484 (class 2606 OID 34897)
-- Name: ticket_resolutions ticket_resolutions_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_resolutions
    ADD CONSTRAINT ticket_resolutions_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(ticket_id) ON DELETE CASCADE;


--
-- TOC entry 5440 (class 2606 OID 34134)
-- Name: tickets tickets_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(user_id);


--
-- TOC entry 5441 (class 2606 OID 34114)
-- Name: tickets tickets_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(asset_id);


--
-- TOC entry 5442 (class 2606 OID 34124)
-- Name: tickets tickets_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(user_id);


--
-- TOC entry 5443 (class 2606 OID 34833)
-- Name: tickets tickets_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id);


--
-- TOC entry 5444 (class 2606 OID 34104)
-- Name: tickets tickets_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5445 (class 2606 OID 34119)
-- Name: tickets tickets_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(user_id);


--
-- TOC entry 5446 (class 2606 OID 34109)
-- Name: tickets tickets_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- TOC entry 5431 (class 2606 OID 34031)
-- Name: user_site_assignments user_site_assignments_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_site_assignments
    ADD CONSTRAINT user_site_assignments_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(user_id);


--
-- TOC entry 5432 (class 2606 OID 34026)
-- Name: user_site_assignments user_site_assignments_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_site_assignments
    ADD CONSTRAINT user_site_assignments_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(site_id) ON DELETE CASCADE;


--
-- TOC entry 5433 (class 2606 OID 34021)
-- Name: user_site_assignments user_site_assignments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_site_assignments
    ADD CONSTRAINT user_site_assignments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 5430 (class 2606 OID 34007)
-- Name: users users_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 5703 (class 0 OID 37669)
-- Dependencies: 264
-- Name: agent_installation_tokens; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.agent_installation_tokens ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5704 (class 0 OID 37705)
-- Dependencies: 265
-- Name: agent_token_usage_history; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.agent_token_usage_history ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5783 (class 3256 OID 37732)
-- Name: agent_token_usage_history agent_token_usage_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_token_usage_insert_policy ON public.agent_token_usage_history FOR INSERT WITH CHECK (true);


--
-- TOC entry 5782 (class 3256 OID 37731)
-- Name: agent_token_usage_history agent_token_usage_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_token_usage_select_policy ON public.agent_token_usage_history FOR SELECT USING ((EXISTS ( SELECT 1
   FROM public.agent_installation_tokens t
  WHERE ((t.token_id = agent_token_usage_history.token_id) AND ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'technician'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (t.client_id = public.current_user_client_id())))))));


--
-- TOC entry 5781 (class 3256 OID 37730)
-- Name: agent_installation_tokens agent_tokens_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_tokens_delete_policy ON public.agent_installation_tokens FOR DELETE USING ((public.current_user_role() = 'superadmin'::public.user_role));


--
-- TOC entry 5779 (class 3256 OID 37728)
-- Name: agent_installation_tokens agent_tokens_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_tokens_insert_policy ON public.agent_installation_tokens FOR INSERT WITH CHECK (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'technician'::public.user_role])) AND (created_by = public.current_user_id())));


--
-- TOC entry 5778 (class 3256 OID 37727)
-- Name: agent_installation_tokens agent_tokens_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_tokens_select_policy ON public.agent_installation_tokens FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'technician'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (client_id = public.current_user_client_id()))));


--
-- TOC entry 5780 (class 3256 OID 37729)
-- Name: agent_installation_tokens agent_tokens_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY agent_tokens_update_policy ON public.agent_installation_tokens FOR UPDATE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'technician'::public.user_role])));


--
-- TOC entry 5685 (class 0 OID 34036)
-- Dependencies: 223
-- Name: assets; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5711 (class 3256 OID 34439)
-- Name: assets assets_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY assets_delete_policy ON public.assets FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5723 (class 3256 OID 34437)
-- Name: assets assets_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY assets_insert_policy ON public.assets FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5722 (class 3256 OID 34436)
-- Name: assets assets_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY assets_select_policy ON public.assets FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id()) OR (site_id = ANY (public.current_user_site_ids()))));


--
-- TOC entry 5724 (class 3256 OID 34438)
-- Name: assets assets_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY assets_update_policy ON public.assets FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (client_id = public.current_user_client_id()))));


--
-- TOC entry 5694 (class 0 OID 34305)
-- Dependencies: 233
-- Name: audit_log; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.audit_log ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5751 (class 3256 OID 34467)
-- Name: audit_log audit_log_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY audit_log_insert_policy ON public.audit_log FOR INSERT WITH CHECK (true);


--
-- TOC entry 5750 (class 3256 OID 34466)
-- Name: audit_log audit_log_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY audit_log_select_policy ON public.audit_log FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR (user_id = public.current_user_id())));


--
-- TOC entry 5681 (class 0 OID 33959)
-- Dependencies: 219
-- Name: clients; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5708 (class 3256 OID 34424)
-- Name: clients clients_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY clients_delete_policy ON public.clients FOR DELETE USING (((public.current_user_role() = 'superadmin'::public.user_role) AND (client_id <> public.current_user_client_id())));


--
-- TOC entry 5706 (class 3256 OID 34422)
-- Name: clients clients_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY clients_insert_policy ON public.clients FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5705 (class 3256 OID 34421)
-- Name: clients clients_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY clients_select_policy ON public.clients FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id())));


--
-- TOC entry 5707 (class 3256 OID 34423)
-- Name: clients clients_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY clients_update_policy ON public.clients FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (client_id = public.current_user_client_id()))));


--
-- TOC entry 5702 (class 0 OID 37391)
-- Dependencies: 258
-- Name: dashboard_widgets; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.dashboard_widgets ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5777 (class 3256 OID 37440)
-- Name: dashboard_widgets dashboard_widgets_own_only; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY dashboard_widgets_own_only ON public.dashboard_widgets TO authenticated USING ((user_id = ( SELECT get_current_user_info.user_id
   FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id))));


--
-- TOC entry 5692 (class 0 OID 34236)
-- Dependencies: 230
-- Name: email_templates; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.email_templates ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5745 (class 3256 OID 34461)
-- Name: email_templates email_templates_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY email_templates_delete_policy ON public.email_templates FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5743 (class 3256 OID 34459)
-- Name: email_templates email_templates_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY email_templates_insert_policy ON public.email_templates FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5742 (class 3256 OID 34458)
-- Name: email_templates email_templates_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY email_templates_select_policy ON public.email_templates FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id()) OR (client_id IS NULL)));


--
-- TOC entry 5744 (class 3256 OID 34460)
-- Name: email_templates email_templates_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY email_templates_update_policy ON public.email_templates FOR UPDATE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5689 (class 0 OID 34161)
-- Dependencies: 227
-- Name: file_attachments; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.file_attachments ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5734 (class 3256 OID 34450)
-- Name: file_attachments file_attachments_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY file_attachments_delete_policy ON public.file_attachments FOR DELETE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR (uploaded_by = public.current_user_id())));


--
-- TOC entry 5733 (class 3256 OID 34449)
-- Name: file_attachments file_attachments_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY file_attachments_insert_policy ON public.file_attachments FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role, 'client_admin'::public.user_role, 'solicitante'::public.user_role])));


--
-- TOC entry 5732 (class 3256 OID 34448)
-- Name: file_attachments file_attachments_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY file_attachments_select_policy ON public.file_attachments FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (uploaded_by = public.current_user_id()) OR (EXISTS ( SELECT 1
   FROM public.tickets t
  WHERE ((t.ticket_id = file_attachments.ticket_id) AND ((t.client_id = public.current_user_client_id()) OR (t.site_id = ANY (public.current_user_site_ids())) OR (t.created_by = public.current_user_id()) OR (t.assigned_to = public.current_user_id())))))));


--
-- TOC entry 5695 (class 0 OID 34319)
-- Dependencies: 234
-- Name: password_reset_tokens; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5756 (class 3256 OID 34471)
-- Name: password_reset_tokens password_reset_tokens_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY password_reset_tokens_delete_policy ON public.password_reset_tokens FOR DELETE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR (user_id = public.current_user_id())));


--
-- TOC entry 5754 (class 3256 OID 34469)
-- Name: password_reset_tokens password_reset_tokens_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY password_reset_tokens_insert_policy ON public.password_reset_tokens FOR INSERT WITH CHECK (true);


--
-- TOC entry 5753 (class 3256 OID 34468)
-- Name: password_reset_tokens password_reset_tokens_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY password_reset_tokens_select_policy ON public.password_reset_tokens FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR (user_id = public.current_user_id())));


--
-- TOC entry 5755 (class 3256 OID 34470)
-- Name: password_reset_tokens password_reset_tokens_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY password_reset_tokens_update_policy ON public.password_reset_tokens FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR (user_id = public.current_user_id())));


--
-- TOC entry 5698 (class 0 OID 37293)
-- Dependencies: 254
-- Name: report_configurations; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.report_configurations ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5771 (class 3256 OID 37434)
-- Name: report_configurations report_configurations_client_own; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_configurations_client_own ON public.report_configurations TO authenticated USING (((client_id = ( SELECT get_current_user_info.client_id
   FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id))) OR (client_id IS NULL)));


--
-- TOC entry 5770 (class 3256 OID 37433)
-- Name: report_configurations report_configurations_superadmin_all; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_configurations_superadmin_all ON public.report_configurations TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id)
  WHERE (get_current_user_info.role = ANY (ARRAY['superadmin'::text, 'admin'::text, 'technician'::text])))));


--
-- TOC entry 5701 (class 0 OID 37370)
-- Dependencies: 257
-- Name: report_deliveries; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.report_deliveries ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5776 (class 3256 OID 37439)
-- Name: report_deliveries report_deliveries_superadmin_all; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_deliveries_superadmin_all ON public.report_deliveries TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id)
  WHERE (get_current_user_info.role = ANY (ARRAY['superadmin'::text, 'admin'::text, 'technician'::text])))));


--
-- TOC entry 5700 (class 0 OID 37342)
-- Dependencies: 256
-- Name: report_executions; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.report_executions ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5775 (class 3256 OID 37438)
-- Name: report_executions report_executions_client_own; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_executions_client_own ON public.report_executions FOR SELECT TO authenticated USING ((config_id IN ( SELECT report_configurations.config_id
   FROM public.report_configurations
  WHERE ((report_configurations.client_id = ( SELECT get_current_user_info.client_id
           FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id))) OR (report_configurations.client_id IS NULL)))));


--
-- TOC entry 5774 (class 3256 OID 37437)
-- Name: report_executions report_executions_superadmin_all; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_executions_superadmin_all ON public.report_executions TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id)
  WHERE (get_current_user_info.role = ANY (ARRAY['superadmin'::text, 'admin'::text, 'technician'::text])))));


--
-- TOC entry 5699 (class 0 OID 37320)
-- Dependencies: 255
-- Name: report_schedules; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.report_schedules ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5773 (class 3256 OID 37436)
-- Name: report_schedules report_schedules_client_own; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_schedules_client_own ON public.report_schedules TO authenticated USING ((config_id IN ( SELECT report_configurations.config_id
   FROM public.report_configurations
  WHERE ((report_configurations.client_id = ( SELECT get_current_user_info.client_id
           FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id))) OR (report_configurations.client_id IS NULL)))));


--
-- TOC entry 5772 (class 3256 OID 37435)
-- Name: report_schedules report_schedules_superadmin_all; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_schedules_superadmin_all ON public.report_schedules TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id)
  WHERE (get_current_user_info.role = ANY (ARRAY['superadmin'::text, 'admin'::text, 'technician'::text])))));


--
-- TOC entry 5697 (class 0 OID 37275)
-- Dependencies: 253
-- Name: report_templates; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.report_templates ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5752 (class 3256 OID 37427)
-- Name: report_templates report_templates_read_all; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_templates_read_all ON public.report_templates FOR SELECT TO authenticated USING ((is_active = true));


--
-- TOC entry 5769 (class 3256 OID 37432)
-- Name: report_templates report_templates_superadmin_all; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY report_templates_superadmin_all ON public.report_templates TO authenticated USING ((EXISTS ( SELECT 1
   FROM public.get_current_user_info() get_current_user_info(user_id, role, client_id)
  WHERE (get_current_user_info.role = ANY (ARRAY['superadmin'::text, 'admin'::text])))));


--
-- TOC entry 5682 (class 0 OID 33973)
-- Dependencies: 220
-- Name: sites; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.sites ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5713 (class 3256 OID 34428)
-- Name: sites sites_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY sites_delete_policy ON public.sites FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5710 (class 3256 OID 34426)
-- Name: sites sites_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY sites_insert_policy ON public.sites FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5709 (class 3256 OID 34425)
-- Name: sites sites_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY sites_select_policy ON public.sites FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id())));


--
-- TOC entry 5712 (class 3256 OID 34427)
-- Name: sites sites_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY sites_update_policy ON public.sites FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (client_id = public.current_user_client_id()))));


--
-- TOC entry 5691 (class 0 OID 34215)
-- Dependencies: 229
-- Name: sla_compliance; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.sla_compliance ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5740 (class 3256 OID 34456)
-- Name: sla_compliance sla_compliance_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY sla_compliance_insert_policy ON public.sla_compliance FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])));


--
-- TOC entry 5739 (class 3256 OID 34455)
-- Name: sla_compliance sla_compliance_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY sla_compliance_select_policy ON public.sla_compliance FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (EXISTS ( SELECT 1
   FROM public.tickets t
  WHERE ((t.ticket_id = sla_compliance.ticket_id) AND ((t.client_id = public.current_user_client_id()) OR (t.site_id = ANY (public.current_user_site_ids()))))))));


--
-- TOC entry 5741 (class 3256 OID 34457)
-- Name: sla_compliance sla_compliance_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY sla_compliance_update_policy ON public.sla_compliance FOR UPDATE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])));


--
-- TOC entry 5690 (class 0 OID 34187)
-- Dependencies: 228
-- Name: slas; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.slas ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5738 (class 3256 OID 34454)
-- Name: slas slas_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY slas_delete_policy ON public.slas FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5736 (class 3256 OID 34452)
-- Name: slas slas_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY slas_insert_policy ON public.slas FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5735 (class 3256 OID 34451)
-- Name: slas slas_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY slas_select_policy ON public.slas FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id())));


--
-- TOC entry 5737 (class 3256 OID 34453)
-- Name: slas slas_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY slas_update_policy ON public.slas FOR UPDATE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5696 (class 0 OID 34335)
-- Dependencies: 235
-- Name: software_licenses; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.software_licenses ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5760 (class 3256 OID 34475)
-- Name: software_licenses software_licenses_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY software_licenses_delete_policy ON public.software_licenses FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5758 (class 3256 OID 34473)
-- Name: software_licenses software_licenses_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY software_licenses_insert_policy ON public.software_licenses FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5757 (class 3256 OID 34472)
-- Name: software_licenses software_licenses_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY software_licenses_select_policy ON public.software_licenses FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id())));


--
-- TOC entry 5759 (class 3256 OID 34474)
-- Name: software_licenses software_licenses_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY software_licenses_update_policy ON public.software_licenses FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (client_id = public.current_user_client_id()))));


--
-- TOC entry 5768 (class 3256 OID 34483)
-- Name: system_config system_config_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY system_config_delete_policy ON public.system_config FOR DELETE USING ((public.current_user_role() = 'superadmin'::public.user_role));


--
-- TOC entry 5766 (class 3256 OID 34481)
-- Name: system_config system_config_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY system_config_insert_policy ON public.system_config FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5765 (class 3256 OID 34480)
-- Name: system_config system_config_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY system_config_select_policy ON public.system_config FOR SELECT USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5767 (class 3256 OID 34482)
-- Name: system_config system_config_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY system_config_update_policy ON public.system_config FOR UPDATE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5693 (class 0 OID 34278)
-- Dependencies: 232
-- Name: technician_assignments; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.technician_assignments ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5749 (class 3256 OID 34465)
-- Name: technician_assignments technician_assignments_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY technician_assignments_delete_policy ON public.technician_assignments FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5747 (class 3256 OID 34463)
-- Name: technician_assignments technician_assignments_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY technician_assignments_insert_policy ON public.technician_assignments FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5746 (class 3256 OID 34462)
-- Name: technician_assignments technician_assignments_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY technician_assignments_select_policy ON public.technician_assignments FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id()) OR (technician_id = public.current_user_id())));


--
-- TOC entry 5748 (class 3256 OID 34464)
-- Name: technician_assignments technician_assignments_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY technician_assignments_update_policy ON public.technician_assignments FOR UPDATE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5686 (class 0 OID 34063)
-- Dependencies: 224
-- Name: ticket_categories; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.ticket_categories ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5764 (class 3256 OID 34479)
-- Name: ticket_categories ticket_categories_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_categories_delete_policy ON public.ticket_categories FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5762 (class 3256 OID 34477)
-- Name: ticket_categories ticket_categories_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_categories_insert_policy ON public.ticket_categories FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5761 (class 3256 OID 34476)
-- Name: ticket_categories ticket_categories_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_categories_select_policy ON public.ticket_categories FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id()) OR (client_id IS NULL)));


--
-- TOC entry 5763 (class 3256 OID 34478)
-- Name: ticket_categories ticket_categories_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_categories_update_policy ON public.ticket_categories FOR UPDATE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5688 (class 0 OID 34139)
-- Dependencies: 226
-- Name: ticket_comments; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.ticket_comments ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5731 (class 3256 OID 34447)
-- Name: ticket_comments ticket_comments_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_comments_delete_policy ON public.ticket_comments FOR DELETE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR (user_id = public.current_user_id())));


--
-- TOC entry 5729 (class 3256 OID 34445)
-- Name: ticket_comments ticket_comments_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_comments_insert_policy ON public.ticket_comments FOR INSERT WITH CHECK (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role, 'client_admin'::public.user_role, 'solicitante'::public.user_role])) AND (EXISTS ( SELECT 1
   FROM public.tickets t
  WHERE ((t.ticket_id = ticket_comments.ticket_id) AND ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (t.client_id = public.current_user_client_id()) OR (t.site_id = ANY (public.current_user_site_ids())) OR (t.created_by = public.current_user_id()) OR (t.assigned_to = public.current_user_id())))))));


--
-- TOC entry 5728 (class 3256 OID 34444)
-- Name: ticket_comments ticket_comments_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_comments_select_policy ON public.ticket_comments FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (EXISTS ( SELECT 1
   FROM public.tickets t
  WHERE ((t.ticket_id = ticket_comments.ticket_id) AND ((t.client_id = public.current_user_client_id()) OR (t.site_id = ANY (public.current_user_site_ids())) OR (t.created_by = public.current_user_id()) OR (t.assigned_to = public.current_user_id())))))));


--
-- TOC entry 5730 (class 3256 OID 34446)
-- Name: ticket_comments ticket_comments_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY ticket_comments_update_policy ON public.ticket_comments FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR (user_id = public.current_user_id())));


--
-- TOC entry 5687 (class 0 OID 34086)
-- Dependencies: 225
-- Name: tickets; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5727 (class 3256 OID 34443)
-- Name: tickets tickets_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tickets_delete_policy ON public.tickets FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5725 (class 3256 OID 34441)
-- Name: tickets tickets_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tickets_insert_policy ON public.tickets FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role, 'client_admin'::public.user_role, 'solicitante'::public.user_role])));


--
-- TOC entry 5718 (class 3256 OID 34440)
-- Name: tickets tickets_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tickets_select_policy ON public.tickets FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id()) OR (site_id = ANY (public.current_user_site_ids())) OR (created_by = public.current_user_id()) OR (assigned_to = public.current_user_id())));


--
-- TOC entry 5726 (class 3256 OID 34442)
-- Name: tickets tickets_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tickets_update_policy ON public.tickets FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (client_id = public.current_user_client_id())) OR (created_by = public.current_user_id()) OR (assigned_to = public.current_user_id())));


--
-- TOC entry 5684 (class 0 OID 34012)
-- Dependencies: 222
-- Name: user_site_assignments; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.user_site_assignments ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5721 (class 3256 OID 34435)
-- Name: user_site_assignments user_site_assignments_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY user_site_assignments_delete_policy ON public.user_site_assignments FOR DELETE USING ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5720 (class 3256 OID 34434)
-- Name: user_site_assignments user_site_assignments_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY user_site_assignments_insert_policy ON public.user_site_assignments FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5719 (class 3256 OID 34433)
-- Name: user_site_assignments user_site_assignments_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY user_site_assignments_select_policy ON public.user_site_assignments FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (user_id = public.current_user_id()) OR (site_id = ANY (public.current_user_site_ids()))));


--
-- TOC entry 5683 (class 0 OID 33993)
-- Dependencies: 221
-- Name: users; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 5717 (class 3256 OID 34432)
-- Name: users users_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY users_delete_policy ON public.users FOR DELETE USING (((public.current_user_role() = 'superadmin'::public.user_role) AND (user_id <> public.current_user_id())));


--
-- TOC entry 5715 (class 3256 OID 34430)
-- Name: users users_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY users_insert_policy ON public.users FOR INSERT WITH CHECK ((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])));


--
-- TOC entry 5714 (class 3256 OID 34429)
-- Name: users users_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY users_select_policy ON public.users FOR SELECT USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role, 'technician'::public.user_role])) OR (client_id = public.current_user_client_id()) OR (user_id = public.current_user_id())));


--
-- TOC entry 5716 (class 3256 OID 34431)
-- Name: users users_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY users_update_policy ON public.users FOR UPDATE USING (((public.current_user_role() = ANY (ARRAY['superadmin'::public.user_role, 'admin'::public.user_role])) OR ((public.current_user_role() = 'client_admin'::public.user_role) AND (client_id = public.current_user_client_id())) OR (user_id = public.current_user_id())));


--
-- TOC entry 5790 (class 0 OID 0)
-- Dependencies: 7
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO app_user;


--
-- TOC entry 5793 (class 0 OID 0)
-- Dependencies: 319
-- Name: FUNCTION armor(bytea); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.armor(bytea) TO app_user;


--
-- TOC entry 5794 (class 0 OID 0)
-- Dependencies: 320
-- Name: FUNCTION armor(bytea, text[], text[]); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.armor(bytea, text[], text[]) TO app_user;


--
-- TOC entry 5795 (class 0 OID 0)
-- Dependencies: 329
-- Name: FUNCTION audit_trigger_function(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.audit_trigger_function() TO app_user;


--
-- TOC entry 5796 (class 0 OID 0)
-- Dependencies: 283
-- Name: FUNCTION crypt(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.crypt(text, text) TO app_user;


--
-- TOC entry 5797 (class 0 OID 0)
-- Dependencies: 327
-- Name: FUNCTION current_user_client_id(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.current_user_client_id() TO app_user;


--
-- TOC entry 5798 (class 0 OID 0)
-- Dependencies: 325
-- Name: FUNCTION current_user_id(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.current_user_id() TO app_user;


--
-- TOC entry 5799 (class 0 OID 0)
-- Dependencies: 326
-- Name: FUNCTION current_user_role(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.current_user_role() TO app_user;


--
-- TOC entry 5800 (class 0 OID 0)
-- Dependencies: 328
-- Name: FUNCTION current_user_site_ids(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.current_user_site_ids() TO app_user;


--
-- TOC entry 5801 (class 0 OID 0)
-- Dependencies: 321
-- Name: FUNCTION dearmor(text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.dearmor(text) TO app_user;


--
-- TOC entry 5802 (class 0 OID 0)
-- Dependencies: 297
-- Name: FUNCTION decrypt(bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.decrypt(bytea, bytea, text) TO app_user;


--
-- TOC entry 5803 (class 0 OID 0)
-- Dependencies: 300
-- Name: FUNCTION decrypt_iv(bytea, bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.decrypt_iv(bytea, bytea, bytea, text) TO app_user;


--
-- TOC entry 5804 (class 0 OID 0)
-- Dependencies: 280
-- Name: FUNCTION digest(bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.digest(bytea, text) TO app_user;


--
-- TOC entry 5805 (class 0 OID 0)
-- Dependencies: 279
-- Name: FUNCTION digest(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.digest(text, text) TO app_user;


--
-- TOC entry 5806 (class 0 OID 0)
-- Dependencies: 290
-- Name: FUNCTION encrypt(bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.encrypt(bytea, bytea, text) TO app_user;


--
-- TOC entry 5807 (class 0 OID 0)
-- Dependencies: 298
-- Name: FUNCTION encrypt_iv(bytea, bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.encrypt_iv(bytea, bytea, bytea, text) TO app_user;


--
-- TOC entry 5808 (class 0 OID 0)
-- Dependencies: 332
-- Name: FUNCTION ensure_single_primary_site(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.ensure_single_primary_site() TO app_user;


--
-- TOC entry 5809 (class 0 OID 0)
-- Dependencies: 301
-- Name: FUNCTION gen_random_bytes(integer); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gen_random_bytes(integer) TO app_user;


--
-- TOC entry 5810 (class 0 OID 0)
-- Dependencies: 302
-- Name: FUNCTION gen_random_uuid(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gen_random_uuid() TO app_user;


--
-- TOC entry 5811 (class 0 OID 0)
-- Dependencies: 284
-- Name: FUNCTION gen_salt(text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gen_salt(text) TO app_user;


--
-- TOC entry 5812 (class 0 OID 0)
-- Dependencies: 285
-- Name: FUNCTION gen_salt(text, integer); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.gen_salt(text, integer) TO app_user;


--
-- TOC entry 5813 (class 0 OID 0)
-- Dependencies: 336
-- Name: FUNCTION generate_agent_token(p_client_id uuid, p_site_id uuid); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.generate_agent_token(p_client_id uuid, p_site_id uuid) TO app_user;


--
-- TOC entry 5814 (class 0 OID 0)
-- Dependencies: 323
-- Name: FUNCTION generate_ticket_number(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.generate_ticket_number() TO app_user;


--
-- TOC entry 5815 (class 0 OID 0)
-- Dependencies: 334
-- Name: FUNCTION get_current_user_info(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.get_current_user_info() TO app_user;


--
-- TOC entry 5816 (class 0 OID 0)
-- Dependencies: 333
-- Name: FUNCTION get_email_routing_recommendation(sender_email text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.get_email_routing_recommendation(sender_email text) TO app_user;


--
-- TOC entry 5817 (class 0 OID 0)
-- Dependencies: 282
-- Name: FUNCTION hmac(bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.hmac(bytea, bytea, text) TO app_user;


--
-- TOC entry 5818 (class 0 OID 0)
-- Dependencies: 281
-- Name: FUNCTION hmac(text, text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.hmac(text, text, text) TO app_user;


--
-- TOC entry 5819 (class 0 OID 0)
-- Dependencies: 322
-- Name: FUNCTION pgp_armor_headers(text, OUT key text, OUT value text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_armor_headers(text, OUT key text, OUT value text) TO app_user;


--
-- TOC entry 5820 (class 0 OID 0)
-- Dependencies: 318
-- Name: FUNCTION pgp_key_id(bytea); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_key_id(bytea) TO app_user;


--
-- TOC entry 5821 (class 0 OID 0)
-- Dependencies: 315
-- Name: FUNCTION pgp_pub_decrypt(bytea, bytea); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_decrypt(bytea, bytea) TO app_user;


--
-- TOC entry 5822 (class 0 OID 0)
-- Dependencies: 276
-- Name: FUNCTION pgp_pub_decrypt(bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_decrypt(bytea, bytea, text) TO app_user;


--
-- TOC entry 5823 (class 0 OID 0)
-- Dependencies: 316
-- Name: FUNCTION pgp_pub_decrypt(bytea, bytea, text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_decrypt(bytea, bytea, text, text) TO app_user;


--
-- TOC entry 5824 (class 0 OID 0)
-- Dependencies: 266
-- Name: FUNCTION pgp_pub_decrypt_bytea(bytea, bytea); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_decrypt_bytea(bytea, bytea) TO app_user;


--
-- TOC entry 5825 (class 0 OID 0)
-- Dependencies: 277
-- Name: FUNCTION pgp_pub_decrypt_bytea(bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_decrypt_bytea(bytea, bytea, text) TO app_user;


--
-- TOC entry 5826 (class 0 OID 0)
-- Dependencies: 317
-- Name: FUNCTION pgp_pub_decrypt_bytea(bytea, bytea, text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_decrypt_bytea(bytea, bytea, text, text) TO app_user;


--
-- TOC entry 5827 (class 0 OID 0)
-- Dependencies: 311
-- Name: FUNCTION pgp_pub_encrypt(text, bytea); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_encrypt(text, bytea) TO app_user;


--
-- TOC entry 5828 (class 0 OID 0)
-- Dependencies: 313
-- Name: FUNCTION pgp_pub_encrypt(text, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_encrypt(text, bytea, text) TO app_user;


--
-- TOC entry 5829 (class 0 OID 0)
-- Dependencies: 312
-- Name: FUNCTION pgp_pub_encrypt_bytea(bytea, bytea); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_encrypt_bytea(bytea, bytea) TO app_user;


--
-- TOC entry 5830 (class 0 OID 0)
-- Dependencies: 314
-- Name: FUNCTION pgp_pub_encrypt_bytea(bytea, bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_pub_encrypt_bytea(bytea, bytea, text) TO app_user;


--
-- TOC entry 5831 (class 0 OID 0)
-- Dependencies: 307
-- Name: FUNCTION pgp_sym_decrypt(bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_decrypt(bytea, text) TO app_user;


--
-- TOC entry 5832 (class 0 OID 0)
-- Dependencies: 309
-- Name: FUNCTION pgp_sym_decrypt(bytea, text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_decrypt(bytea, text, text) TO app_user;


--
-- TOC entry 5833 (class 0 OID 0)
-- Dependencies: 308
-- Name: FUNCTION pgp_sym_decrypt_bytea(bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_decrypt_bytea(bytea, text) TO app_user;


--
-- TOC entry 5834 (class 0 OID 0)
-- Dependencies: 310
-- Name: FUNCTION pgp_sym_decrypt_bytea(bytea, text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_decrypt_bytea(bytea, text, text) TO app_user;


--
-- TOC entry 5835 (class 0 OID 0)
-- Dependencies: 303
-- Name: FUNCTION pgp_sym_encrypt(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_encrypt(text, text) TO app_user;


--
-- TOC entry 5836 (class 0 OID 0)
-- Dependencies: 305
-- Name: FUNCTION pgp_sym_encrypt(text, text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_encrypt(text, text, text) TO app_user;


--
-- TOC entry 5837 (class 0 OID 0)
-- Dependencies: 304
-- Name: FUNCTION pgp_sym_encrypt_bytea(bytea, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_encrypt_bytea(bytea, text) TO app_user;


--
-- TOC entry 5838 (class 0 OID 0)
-- Dependencies: 306
-- Name: FUNCTION pgp_sym_encrypt_bytea(bytea, text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pgp_sym_encrypt_bytea(bytea, text, text) TO app_user;


--
-- TOC entry 5839 (class 0 OID 0)
-- Dependencies: 324
-- Name: FUNCTION set_ticket_number(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.set_ticket_number() TO app_user;


--
-- TOC entry 5840 (class 0 OID 0)
-- Dependencies: 330
-- Name: FUNCTION test_rls_policies(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.test_rls_policies() TO app_user;


--
-- TOC entry 5841 (class 0 OID 0)
-- Dependencies: 331
-- Name: FUNCTION update_updated_at_column(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_updated_at_column() TO app_user;


--
-- TOC entry 5842 (class 0 OID 0)
-- Dependencies: 272
-- Name: FUNCTION uuid_generate_v1(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v1() TO app_user;


--
-- TOC entry 5843 (class 0 OID 0)
-- Dependencies: 273
-- Name: FUNCTION uuid_generate_v1mc(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v1mc() TO app_user;


--
-- TOC entry 5844 (class 0 OID 0)
-- Dependencies: 274
-- Name: FUNCTION uuid_generate_v3(namespace uuid, name text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v3(namespace uuid, name text) TO app_user;


--
-- TOC entry 5845 (class 0 OID 0)
-- Dependencies: 275
-- Name: FUNCTION uuid_generate_v4(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v4() TO app_user;


--
-- TOC entry 5846 (class 0 OID 0)
-- Dependencies: 278
-- Name: FUNCTION uuid_generate_v5(namespace uuid, name text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v5(namespace uuid, name text) TO app_user;


--
-- TOC entry 5847 (class 0 OID 0)
-- Dependencies: 267
-- Name: FUNCTION uuid_nil(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_nil() TO app_user;


--
-- TOC entry 5848 (class 0 OID 0)
-- Dependencies: 268
-- Name: FUNCTION uuid_ns_dns(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_dns() TO app_user;


--
-- TOC entry 5849 (class 0 OID 0)
-- Dependencies: 270
-- Name: FUNCTION uuid_ns_oid(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_oid() TO app_user;


--
-- TOC entry 5850 (class 0 OID 0)
-- Dependencies: 269
-- Name: FUNCTION uuid_ns_url(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_url() TO app_user;


--
-- TOC entry 5851 (class 0 OID 0)
-- Dependencies: 271
-- Name: FUNCTION uuid_ns_x500(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_x500() TO app_user;


--
-- TOC entry 5852 (class 0 OID 0)
-- Dependencies: 335
-- Name: FUNCTION validate_agent_token(p_token_value character varying); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.validate_agent_token(p_token_value character varying) TO app_user;


--
-- TOC entry 5853 (class 0 OID 0)
-- Dependencies: 264
-- Name: TABLE agent_installation_tokens; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.agent_installation_tokens TO app_user;


--
-- TOC entry 5854 (class 0 OID 0)
-- Dependencies: 265
-- Name: TABLE agent_token_usage_history; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.agent_token_usage_history TO app_user;


--
-- TOC entry 5855 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE assets; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.assets TO app_user;


--
-- TOC entry 5856 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE audit_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.audit_log TO app_user;


--
-- TOC entry 5857 (class 0 OID 0)
-- Dependencies: 238
-- Name: TABLE categories; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.categories TO app_user;


--
-- TOC entry 5858 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE clients; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.clients TO app_user;


--
-- TOC entry 5859 (class 0 OID 0)
-- Dependencies: 258
-- Name: TABLE dashboard_widgets; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.dashboard_widgets TO app_user;


--
-- TOC entry 5861 (class 0 OID 0)
-- Dependencies: 239
-- Name: TABLE email_configurations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_configurations TO app_user;


--
-- TOC entry 5862 (class 0 OID 0)
-- Dependencies: 241
-- Name: TABLE email_processing_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_processing_log TO app_user;


--
-- TOC entry 5863 (class 0 OID 0)
-- Dependencies: 240
-- Name: TABLE email_queue; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_queue TO app_user;


--
-- TOC entry 5864 (class 0 OID 0)
-- Dependencies: 248
-- Name: TABLE email_routing_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_routing_log TO app_user;


--
-- TOC entry 5865 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE sites; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sites TO app_user;


--
-- TOC entry 5866 (class 0 OID 0)
-- Dependencies: 249
-- Name: TABLE email_routing_analysis; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_routing_analysis TO app_user;


--
-- TOC entry 5867 (class 0 OID 0)
-- Dependencies: 247
-- Name: TABLE email_routing_rules; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_routing_rules TO app_user;


--
-- TOC entry 5868 (class 0 OID 0)
-- Dependencies: 251
-- Name: TABLE email_routing_sites_view; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_routing_sites_view TO app_user;


--
-- TOC entry 5869 (class 0 OID 0)
-- Dependencies: 230
-- Name: TABLE email_templates; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_templates TO app_user;


--
-- TOC entry 5870 (class 0 OID 0)
-- Dependencies: 250
-- Name: TABLE email_templates_view; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.email_templates_view TO app_user;


--
-- TOC entry 5871 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE file_attachments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.file_attachments TO app_user;


--
-- TOC entry 5872 (class 0 OID 0)
-- Dependencies: 246
-- Name: TABLE notification_queue; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.notification_queue TO app_user;


--
-- TOC entry 5873 (class 0 OID 0)
-- Dependencies: 252
-- Name: TABLE notification_tracking; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.notification_tracking TO app_user;


--
-- TOC entry 5874 (class 0 OID 0)
-- Dependencies: 234
-- Name: TABLE password_reset_tokens; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.password_reset_tokens TO app_user;


--
-- TOC entry 5876 (class 0 OID 0)
-- Dependencies: 254
-- Name: TABLE report_configurations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_configurations TO app_user;


--
-- TOC entry 5877 (class 0 OID 0)
-- Dependencies: 260
-- Name: TABLE report_configurations_backup; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_configurations_backup TO app_user;


--
-- TOC entry 5878 (class 0 OID 0)
-- Dependencies: 257
-- Name: TABLE report_deliveries; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_deliveries TO app_user;


--
-- TOC entry 5879 (class 0 OID 0)
-- Dependencies: 263
-- Name: TABLE report_deliveries_backup; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_deliveries_backup TO app_user;


--
-- TOC entry 5881 (class 0 OID 0)
-- Dependencies: 256
-- Name: TABLE report_executions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_executions TO app_user;


--
-- TOC entry 5882 (class 0 OID 0)
-- Dependencies: 262
-- Name: TABLE report_executions_backup; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_executions_backup TO app_user;


--
-- TOC entry 5884 (class 0 OID 0)
-- Dependencies: 255
-- Name: TABLE report_schedules; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_schedules TO app_user;


--
-- TOC entry 5885 (class 0 OID 0)
-- Dependencies: 261
-- Name: TABLE report_schedules_backup; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_schedules_backup TO app_user;


--
-- TOC entry 5887 (class 0 OID 0)
-- Dependencies: 253
-- Name: TABLE report_templates; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_templates TO app_user;


--
-- TOC entry 5888 (class 0 OID 0)
-- Dependencies: 259
-- Name: TABLE report_templates_backup; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.report_templates_backup TO app_user;


--
-- TOC entry 5889 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE sla_compliance; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sla_compliance TO app_user;


--
-- TOC entry 5890 (class 0 OID 0)
-- Dependencies: 242
-- Name: TABLE sla_policies; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sla_policies TO app_user;


--
-- TOC entry 5891 (class 0 OID 0)
-- Dependencies: 243
-- Name: TABLE sla_tracking; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sla_tracking TO app_user;


--
-- TOC entry 5892 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE slas; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.slas TO app_user;


--
-- TOC entry 5893 (class 0 OID 0)
-- Dependencies: 235
-- Name: TABLE software_licenses; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.software_licenses TO app_user;


--
-- TOC entry 5895 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE system_config; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.system_config TO app_user;


--
-- TOC entry 5896 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE technician_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.technician_assignments TO app_user;


--
-- TOC entry 5897 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE ticket_activities; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.ticket_activities TO app_user;


--
-- TOC entry 5898 (class 0 OID 0)
-- Dependencies: 245
-- Name: TABLE ticket_attachments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.ticket_attachments TO app_user;


--
-- TOC entry 5899 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE ticket_categories; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.ticket_categories TO app_user;


--
-- TOC entry 5900 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE ticket_comments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.ticket_comments TO app_user;


--
-- TOC entry 5901 (class 0 OID 0)
-- Dependencies: 236
-- Name: SEQUENCE ticket_number_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.ticket_number_seq TO app_user;


--
-- TOC entry 5902 (class 0 OID 0)
-- Dependencies: 244
-- Name: TABLE ticket_resolutions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.ticket_resolutions TO app_user;


--
-- TOC entry 5905 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE tickets; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.tickets TO app_user;


--
-- TOC entry 5906 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE user_site_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.user_site_assignments TO app_user;


--
-- TOC entry 5907 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.users TO app_user;


--
-- TOC entry 2305 (class 826 OID 34485)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,USAGE ON SEQUENCES TO app_user;


--
-- TOC entry 2306 (class 826 OID 34486)
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO app_user;


--
-- TOC entry 2304 (class 826 OID 34484)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO app_user;


-- Completed on 2025-07-20 20:26:24

--
-- PostgreSQL database dump complete
--

