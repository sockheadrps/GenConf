import { writable } from 'svelte/store';

// Define the store to hold the fuel estimate data and loading state
export const fuelEstimate = writable({
  data: null,
  loading: false,
  error: null
});

// Function to fetch fuel estimate
export async function getFuelEstimate() {
  fuelEstimate.set({ data: null, loading: true, error: null }); // Start loading
  try {
    const uri = `http://127.0.0.1:8100/gen_fuel_estimate/december`;
    const response = await fetch(uri);
    if (!response.ok) {
      throw new Error('Failed to fetch data');
    }
    const data = await response.json();
    fuelEstimate.set({ data, loading: false, error: null }); // Update store with data
  } catch (error) {
    fuelEstimate.set({ data: null, loading: false, error: error.message }); // Handle error
  }
}