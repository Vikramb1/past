#!/usr/bin/env node

// Simple database connection test
import { createClient } from '@supabase/supabase-js';

// Hardcoded configuration
const SUPABASE_URL = 'https://afwpcbmhvjwrnolhrocz.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmd3BjYm1odmp3cm5vbGhyb2N6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTM2NzYwOCwiZXhwIjoyMDc2OTQzNjA4fQ.32C1dNH0-aQFhpODSlw9UzAj721kjP_BIZfuS-2VMGE';

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

console.log("🔍 Testing Supabase Database Connection\n");
console.log("URL:", SUPABASE_URL);
console.log("Key:", SUPABASE_SERVICE_KEY.substring(0, 20) + "...\n");

async function testDatabase() {
  try {
    // Test 1: Check nyne_results table
    console.log("📊 Testing nyne_results table:");
    const { data: nyneData, error: nyneError } = await supabase
      .from('nyne_results')
      .select('email, name, company')
      .limit(3);

    if (nyneError) {
      console.log("❌ Error accessing nyne_results:", nyneError.message);
    } else {
      console.log(`✅ Found ${nyneData?.length || 0} records`);
      if (nyneData && nyneData.length > 0) {
        console.log("Sample records:");
        nyneData.forEach(record => {
          console.log(`  - ${record.name || 'No name'} (${record.email}) - ${record.company || 'No company'}`);
        });
      }
    }
    console.log("");

    // Test 2: Check images_names table
    console.log("🖼️  Testing images_names table:");
    const { data: imageData, error: imageError } = await supabase
      .from('images_names')
      .select('email')
      .limit(3);

    if (imageError) {
      console.log("❌ Error accessing images_names:", imageError.message);
    } else {
      console.log(`✅ Found ${imageData?.length || 0} records with images`);
      if (imageData && imageData.length > 0) {
        console.log("Sample emails with images:");
        imageData.forEach(record => {
          console.log(`  - ${record.email}`);
        });
      }
    }
    console.log("");

    // Test 3: Test search functionality
    console.log("🔍 Testing search capabilities:");
    const searchTests = [
      { field: 'name', value: 'John', description: 'Searching for names containing "John"' },
      { field: 'company', value: 'Tech', description: 'Searching for companies containing "Tech"' },
      { field: 'location', value: 'San Francisco', description: 'Searching for location "San Francisco"' }
    ];

    for (const test of searchTests) {
      console.log(`\n  ${test.description}:`);
      const { data, error } = await supabase
        .from('nyne_results')
        .select('email, name')
        .ilike(test.field, `%${test.value}%`)
        .limit(2);

      if (error) {
        console.log(`  ❌ Error: ${error.message}`);
      } else {
        console.log(`  ✅ Found ${data?.length || 0} matches`);
        if (data && data.length > 0) {
          data.forEach(record => {
            console.log(`     - ${record.name || 'No name'} (${record.email})`);
          });
        }
      }
    }

    console.log("\n✅ Database connection test completed!");

  } catch (error) {
    console.error("\n❌ Fatal error:", error);
  }
}

testDatabase();