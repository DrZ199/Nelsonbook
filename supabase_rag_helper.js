/**
 * Supabase RAG Helper for Nelson Pediatrics Database
 * 
 * This file provides helper functions for querying the Nelson Pediatrics database
 * in Supabase for RAG (Retrieval Augmented Generation) applications.
 */

import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Search for content using full-text search
 * @param {string} query - The search query
 * @param {number} limit - Maximum number of results to return
 * @returns {Promise<Array>} - Array of matching content blocks
 */
export async function searchByText(query, limit = 10) {
  const { data, error } = await supabase
    .from('nelson_content')
    .select(`
      id,
      title,
      content_text,
      content_type,
      nelson_chapters(chapter_number, title),
      nelson_sections(section_number, title),
      nelson_subsections(subsection_number, title)
    `)
    .textSearch('content_text', query)
    .limit(limit);

  if (error) {
    console.error('Error searching content:', error);
    throw error;
  }

  return data;
}

/**
 * Search for content using vector similarity
 * @param {Array<number>} embedding - The query embedding vector
 * @param {number} limit - Maximum number of results to return
 * @param {number} threshold - Similarity threshold (0-1)
 * @returns {Promise<Array>} - Array of matching content blocks
 */
export async function searchBySimilarity(embedding, limit = 10, threshold = 0.7) {
  const { data, error } = await supabase.rpc(
    'match_nelson_content',
    {
      query_embedding: embedding,
      match_threshold: threshold,
      match_count: limit
    }
  );

  if (error) {
    console.error('Error searching by similarity:', error);
    throw error;
  }

  return data;
}

/**
 * Get drug information by name
 * @param {string} drugName - The drug name to search for
 * @returns {Promise<Array>} - Array of matching drugs with dosages
 */
export async function getDrugInfo(drugName) {
  const { data, error } = await supabase
    .from('nelson_drugs')
    .select(`
      id,
      drug_name,
      drug_brand_name,
      drug_formulations,
      drug_indication,
      drug_mechanism,
      drug_adverse_effects,
      drug_contraindications,
      nelson_content(title, content_text),
      nelson_dosages(*)
    `)
    .ilike('drug_name', `%${drugName}%`)
    .limit(10);

  if (error) {
    console.error('Error getting drug info:', error);
    throw error;
  }

  return data;
}

/**
 * Get dosage information for a specific drug and age group
 * @param {string} drugName - The drug name to search for
 * @param {string} ageGroup - The age group (e.g., "CHILDREN 7-11 YR")
 * @returns {Promise<Array>} - Array of matching dosages
 */
export async function getDosageInfo(drugName, ageGroup) {
  const { data, error } = await supabase
    .from('nelson_dosages')
    .select(`
      id,
      age_group,
      route,
      value,
      max_dose,
      frequency,
      special_considerations,
      nelson_drugs!inner(drug_name, drug_brand_name, drug_formulations)
    `)
    .eq('nelson_drugs.drug_name', drugName)
    .ilike('age_group', `%${ageGroup}%`)
    .limit(10);

  if (error) {
    console.error('Error getting dosage info:', error);
    throw error;
  }

  return data;
}

/**
 * Get content by type (e.g., epidemiology, clinical_manifestations)
 * @param {string} contentType - The content type to search for
 * @param {string} query - Optional search query within the content type
 * @param {number} limit - Maximum number of results to return
 * @returns {Promise<Array>} - Array of matching content blocks
 */
export async function getContentByType(contentType, query = '', limit = 10) {
  let queryBuilder = supabase
    .from('nelson_content')
    .select(`
      id,
      title,
      content_text,
      content_type,
      nelson_chapters(chapter_number, title),
      nelson_sections(section_number, title),
      nelson_subsections(subsection_number, title)
    `)
    .eq('content_type', contentType)
    .limit(limit);

  if (query) {
    queryBuilder = queryBuilder.textSearch('content_text', query);
  }

  const { data, error } = await queryBuilder;

  if (error) {
    console.error('Error getting content by type:', error);
    throw error;
  }

  return data;
}

/**
 * Get hierarchical content structure (chapters, sections, subsections)
 * @returns {Promise<Array>} - Array of chapters with nested sections and subsections
 */
export async function getContentStructure() {
  const { data, error } = await supabase
    .from('nelson_chapters')
    .select(`
      id,
      chapter_number,
      title,
      nelson_sections(
        id,
        section_number,
        title,
        nelson_subsections(
          id,
          subsection_number,
          title
        )
      )
    `)
    .order('chapter_number', { ascending: true });

  if (error) {
    console.error('Error getting content structure:', error);
    throw error;
  }

  return data;
}

/**
 * Create a stored procedure for vector similarity search in Supabase
 * This function should be run once to set up the vector search capability
 */
export async function createMatchFunction() {
  const { error } = await supabase.rpc('create_match_function');

  if (error) {
    console.error('Error creating match function:', error);
    throw error;
  }

  console.log('Match function created successfully');
}

/**
 * SQL to create the match function in Supabase
 * Run this in the Supabase SQL editor
 */
export const MATCH_FUNCTION_SQL = `
-- Create a function to match content by vector similarity
CREATE OR REPLACE FUNCTION match_nelson_content(
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
  title text,
  content_text text,
  content_type text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    nelson_content.id,
    nelson_content.title,
    nelson_content.content_text,
    nelson_content.content_type,
    1 - (nelson_content.content_embedding <=> query_embedding) AS similarity
  FROM nelson_content
  WHERE 1 - (nelson_content.content_embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
`;

/**
 * Example usage in a RAG application
 */
export async function exampleRagQuery(userQuery, openaiApiKey) {
  try {
    // 1. Get embedding for user query using OpenAI
    const response = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openaiApiKey}`
      },
      body: JSON.stringify({
        input: userQuery,
        model: 'text-embedding-ada-002'
      })
    });

    const embeddingData = await response.json();
    const embedding = embeddingData.data[0].embedding;

    // 2. Search for relevant content using vector similarity
    const relevantContent = await searchBySimilarity(embedding, 5, 0.7);

    // 3. Format content for RAG
    const context = relevantContent.map(item => {
      return `
Title: ${item.title}
Type: ${item.content_type}
Content: ${item.content_text}
Similarity: ${item.similarity}
---
`;
    }).join('\n');

    // 4. Return formatted context for use in RAG
    return {
      relevantContent,
      formattedContext: context
    };
  } catch (error) {
    console.error('Error in RAG query:', error);
    throw error;
  }
}

