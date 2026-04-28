import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

serve(async (req) => {
  try {
    const { record, old_record } = await req.json();

    // Only process authenticated users
    if (!record || !record.id) {
      return new Response(JSON.stringify(record), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // Get restaurant staff information for this user
    const { data: staffData, error } = await supabase
      .from("restaurant_staff")
      .select("restaurant_id, role, permissions, is_active")
      .eq("user_id", record.id)
      .eq("is_active", true)
      .single();

    let customClaims = {
      restaurant_id: null,
      role: "customer",
      permissions: {},
    };

    // If user is restaurant staff, add their claims
    if (staffData && !error) {
      customClaims = {
        restaurant_id: staffData.restaurant_id,
        role: staffData.role,
        permissions: staffData.permissions || {},
      };
    }

    // Merge with existing user metadata
    const response = {
      ...record,
      raw_user_meta_data: {
        ...record.raw_user_meta_data,
        ...customClaims,
      },
      app_metadata: {
        ...record.app_metadata,
        ...customClaims,
      },
    };

    return new Response(JSON.stringify(response), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in custom claims function:", error);

    // Return original record on error
    const { record } = await req.json();
    return new Response(JSON.stringify(record), {
      headers: { "Content-Type": "application/json" },
    });
  }
});