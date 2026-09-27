require("dotenv").config();

const { createClient } = require("@supabase/supabase-js");

const supabase = createClient("https://dummy.supabase.co", "dummy-key");

module.exports = supabase;
