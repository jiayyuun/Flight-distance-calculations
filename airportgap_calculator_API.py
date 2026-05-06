import pandas as pd
import requests
import json
from typing import List, Dict, Optional
import sys

class AirportGapCalculator:
    """
    Calculate flight distances using the Airport Gap API.
    Returns pure Great Circle Distance.
    """
    
    def __init__(self, api_token: Optional[str] = None):
        self.base_url = "https://airportgap.com/api"
        self.api_token = api_token
        self.headers = {}
        
        if api_token:
            self.headers["Authorization"] = f"Bearer token={api_token}"
        
        print("Airport Gap API client initialized")
        if not api_token:
            print("  Note: No API token provided. Distance endpoint works without auth.")
            #print("  Get a free token at: https://airportgap.com/tokens/new")
    
    def calculate_distance(self, origin: str, destination: str) -> Dict:
        
        # Build request
        payload = {
            "from": origin.upper(),
            "to": destination.upper()
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/airports/distance",
                data=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract data from JSON:API format
            if 'data' in data and 'attributes' in data['data']:
                attrs = data['data']['attributes']
                
                return {
                    'origin_code': origin.upper(),
                    'origin_airport': attrs.get('from_airport', {}),
                    'destination_code': destination.upper(),
                    'destination_airport': attrs.get('to_airport', {}),
                    'distance_km': attrs.get('kilometers', 0)
                }
            else:
                raise Exception("Unexpected API response format")
                
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise Exception(f"Airport code not found: {origin} or {destination}")
            elif response.status_code == 422:
                raise Exception("Invalid request parameters")
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded (100 requests/minute)")
            else:
                raise Exception(f"HTTP {response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def extract_airport_code(self, text: str) -> str:
       #Returns just the airport code
        if pd.isna(text):
            return ''
        
        text = str(text).strip()
        
        # Check if there's a code in brackets [CODE]
        if '[' in text and ']' in text:
            start = text.find('[')
            end = text.find(']')
            code = text[start+1:end].strip()
            return code
        
        # If no brackets, assume the whole text is the code
        return text
    
    def process_csv(self, csv_filepath: str, output_filepath: str = None) -> pd.DataFrame:
        """
        Expected CSV format:
        origin,destination
        """
        
        # Read CSV
        try:
            df = pd.read_csv(csv_filepath)
        except FileNotFoundError:
            print(f"Error: File '{csv_filepath}' not found!")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return pd.DataFrame()
        
        # Validate columns
        if 'origin' not in df.columns or 'destination' not in df.columns:
            print("Error: CSV must have 'origin' and 'destination' columns!")
            print(f"   Found columns: {', '.join(df.columns)}")
            return pd.DataFrame()
        
        print(f"Found {len(df)} flights to process")
        
        # Convert to list of dicts
        flights = df.to_dict('records')
        
        # Process flights
        results_df = self.process_flight_data(flights)
        
        # Save to CSV
        if output_filepath is None:
            output_filepath = csv_filepath.replace('.csv', '_distances.csv')
        
        results_df.to_csv(output_filepath, index=False)
        print(f"\nResults saved to: {output_filepath}")
        
        return results_df
    
    def process_flight_data(self, flights_data: List[Dict]) -> pd.DataFrame:
        results = []
        
        print("\n" + "="*80)
        print("PROCESSING FLIGHTS")
        print("="*80 + "\n")
        
        for i, flight in enumerate(flights_data, 1):
            try:
                # Extract airport codes
                origin_raw = flight.get('origin', '')
                destination_raw = flight.get('destination', '')
                
                # Clean and extract IATA codes
                origin = self.extract_airport_code(origin_raw)
                destination = self.extract_airport_code(destination_raw)
                
                if not origin or not destination:
                    raise Exception(f"Could not extract airport codes from: {origin_raw} → {destination_raw}")
                
                # Call Airport Gap API
                distance_info = self.calculate_distance(origin, destination)
                
                # Get origin airport details
                from_airport = distance_info.get('origin_airport', {})
                to_airport = distance_info.get('destination_airport', {})
                
                # Combine original data with distance calculation
                result = {
                    'origin_raw': origin_raw,  # Keep original text
                    'destination_raw': destination_raw,  # Keep original text
                    'origin_code': origin.upper(),
                    'origin_name': from_airport.get('name', ''),
                    'origin_city': from_airport.get('city', ''),
                    'origin_country': from_airport.get('country', ''),
                    'destination_code': destination.upper(),
                    'destination_name': to_airport.get('name', ''),
                    'destination_city': to_airport.get('city', ''),
                    'destination_country': to_airport.get('country', ''),
                    'distance_km': distance_info['distance_km']
                }
                
                print(f" Distance: {result['distance_km']} km")
                
                results.append(result)
                
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                result = {
                    'origin_raw': flight.get('origin', ''),
                    'destination_raw': flight.get('destination', ''),
                    'error': str(e)
                }
                results.append(result)
        
        print("\n" + "="*80)
        print(f"✓ Processed {len(results)} flights")
        print("="*80)
        
        return pd.DataFrame(results)


# Example usage
if __name__ == "__main__":
    # Hardcode your CSV file
    csv_file = "data.csv"
    output_file = "data_distances.csv"
    
    calc = AirportGapCalculator()
    results_df = calc.process_csv(csv_file, output_file)
    
    # Check if CSV file provided as argument
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        results_df = calc.process_csv(csv_file, output_file)
    else:
        # Example: Create a sample CSV and process it
        print("\n📝 No CSV file provided.")
        
        # Process the sample
        results_df = calc.process_csv('sample_flights.csv')
        
        # Display results
        if not results_df.empty:
            print("\n" + "="*80)
            print("SAMPLE RESULTS:")
            print("="*80)
            display_cols = ['origin_code', 'destination_code', 'distance_km']
            if 'error' in results_df.columns:
                display_cols.append('error')
            print(results_df[display_cols].to_string(index=False))
            
            print("\nUsage:")
            print("   python airportgap_calculator.py your_flights.csv")
            print("   python airportgap_calculator.py your_flights.csv output.csv")