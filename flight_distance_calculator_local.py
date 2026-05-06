import pandas as pd
from math import radians, sin, cos, sqrt, atan2

class FlightDistanceCalculator:
    """
    Calculate Great Circle Distance (GCD) between airports using IATA codes.
    Returns pure GCD without any uplift factors.
    """
    
    def __init__(self):
        # Built-in airport database with major airports
        # Format: 'IATA': (latitude, longitude, name, city, country)
        self.airports = {
            # Africa
            'ABJ': (5.2539, -3.9263, 'Felix Houphouet-Boigny International Airport', 'Abidjan', 'Ivory Coast'),
            'LOS': (6.5774, 3.3213, 'Murtala Muhammed International Airport', 'Lagos', 'Nigeria'),
            'CAI': (30.1127, 31.4000, 'Cairo International Airport', 'Cairo', 'Egypt'),
            'JNB': (-26.1392, 28.2460, 'O.R. Tambo International Airport', 'Johannesburg', 'South Africa'),
            'CPT': (-33.9715, 18.6021, 'Cape Town International Airport', 'Cape Town', 'South Africa'),
            'ADD': (8.9806, 38.7994, 'Addis Ababa Bole International Airport', 'Addis Ababa', 'Ethiopia'),
            'NBO': (-1.3192, 36.9278, 'Jomo Kenyatta International Airport', 'Nairobi', 'Kenya'),
            'ACC': (5.6052, -0.1719, 'Kotoka International Airport', 'Accra', 'Ghana'),
            'ALG': (36.6910, 3.2154, 'Houari Boumediene Airport', 'Algiers', 'Algeria'),
            'TUN': (36.8510, 10.2272, 'Tunis-Carthage International Airport', 'Tunis', 'Tunisia'),
            
            # Europe
            'LHR': (51.4700, -0.4543, 'London Heathrow Airport', 'London', 'United Kingdom'),
            'CDG': (49.0097, 2.5479, 'Charles de Gaulle Airport', 'Paris', 'France'),
            'FRA': (50.0379, 8.5622, 'Frankfurt Airport', 'Frankfurt', 'Germany'),
            'AMS': (52.3086, 4.7639, 'Amsterdam Airport Schiphol', 'Amsterdam', 'Netherlands'),
            'MAD': (40.4936, -3.5668, 'Madrid-Barajas Airport', 'Madrid', 'Spain'),
            'FCO': (41.8003, 12.2389, 'Leonardo da Vinci-Fiumicino Airport', 'Rome', 'Italy'),
            'IST': (41.2753, 28.7519, 'Istanbul Airport', 'Istanbul', 'Turkey'),
            'CPH': (55.6181, 12.6561, 'Copenhagen Airport', 'Copenhagen', 'Denmark'),
            'DBV': (42.5614, 18.2682, 'Dubrovnik Airport', 'Dubrovnik', 'Croatia'),
            
            # North America
            'JFK': (40.6413, -73.7781, 'John F. Kennedy International Airport', 'New York', 'USA'),
            'LAX': (33.9416, -118.4085, 'Los Angeles International Airport', 'Los Angeles', 'USA'),
            'ORD': (41.9742, -87.9073, "O'Hare International Airport", 'Chicago', 'USA'),
            'ATL': (33.6407, -84.4277, 'Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'USA'),
            'MIA': (25.7959, -80.2870, 'Miami International Airport', 'Miami', 'USA'),
            'YYZ': (43.6777, -79.6248, 'Toronto Pearson International Airport', 'Toronto', 'Canada'),
            
            # Asia
            'DXB': (25.2532, 55.3657, 'Dubai International Airport', 'Dubai', 'UAE'),
            'SIN': (1.3644, 103.9915, 'Singapore Changi Airport', 'Singapore', 'Singapore'),
            'HKG': (22.3080, 113.9185, 'Hong Kong International Airport', 'Hong Kong', 'Hong Kong'),
            'NRT': (35.7720, 140.3929, 'Narita International Airport', 'Tokyo', 'Japan'),
            'PEK': (40.0799, 116.6031, 'Beijing Capital International Airport', 'Beijing', 'China'),
            'BKK': (13.6900, 100.7501, 'Suvarnabhumi Airport', 'Bangkok', 'Thailand'),
            'DEL': (28.5562, 77.1000, 'Indira Gandhi International Airport', 'Delhi', 'India'),
            'DOH': (25.2736, 51.6081, 'Hamad International Airport', 'Doha', 'Qatar'),
            'SUB': (-7.3798, 112.7873, 'Juanda International Airport', 'Surabaya', 'Indonesia'),
            'SZX': (22.6393, 113.8107, 'Shenzhen Bao\'an International Airport', 'Shenzhen', 'China'),
            'CAN': (23.3924, 113.2988, 'Guangzhou Baiyun International Airport', 'Guangzhou', 'China'),
            'CGK': (-6.1256, 106.6559, 'Soekarno-Hatta International Airport', 'Jakarta', 'Indonesia'),
            
            # South America
            'GRU': (-23.4321, -46.4695, 'São Paulo–Guarulhos International Airport', 'São Paulo', 'Brazil'),
            'CGH': (-23.6261, -46.6564, 'Congonhas Airport', 'São Paulo', 'Brazil'),
            'GIG': (-22.8099, -43.2505, 'Rio de Janeiro/Galeão International Airport', 'Rio de Janeiro', 'Brazil'),
            'EZE': (-34.8222, -58.5358, 'Ministro Pistarini International Airport', 'Buenos Aires', 'Argentina'),
            'BOG': (4.7016, -74.1469, 'El Dorado International Airport', 'Bogotá', 'Colombia'),
            'SCL': (-33.3929, -70.7858, 'Arturo Merino Benítez International Airport', 'Santiago', 'Chile'),
            
            # Oceania
            'SYD': (-33.9399, 151.1753, 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia'),
            'MEL': (-37.6690, 144.8410, 'Melbourne Airport', 'Melbourne', 'Australia'),
            'AKL': (-37.0082, 174.7850, 'Auckland Airport', 'Auckland', 'New Zealand'),
        }
        
        print(f"Loaded {len(self.airports)} airports into database")
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the Great Circle Distance between two points on Earth.
        Uses the Haversine formula.
        
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        return round(distance, 2)
    
    def get_airport_info(self, iata_code):
        """
        Get airport information by IATA code
        """
        iata = iata_code.upper()
        if iata in self.airports:
            lat, lon, name, city, country = self.airports[iata]
            return {
                'latitude': lat,
                'longitude': lon,
                'name': name,
                'city': city,
                'country': country
            }
        else:
            return None
    
    def calculate_distance(self, origin_iata, destination_iata):
        origin = self.get_airport_info(origin_iata)
        destination = self.get_airport_info(destination_iata)
        
        if not origin:
            raise ValueError(f"Airport code '{origin_iata}' not found in database. Available codes: {', '.join(sorted(self.airports.keys()))}")
        if not destination:
            raise ValueError(f"Airport code '{destination_iata}' not found in database. Available codes: {', '.join(sorted(self.airports.keys()))}")
        
        distance = self.haversine_distance(
            origin['latitude'], origin['longitude'],
            destination['latitude'], destination['longitude']
        )
        
        return {
            'origin_code': origin_iata.upper(),
            'origin_name': origin['name'],
            'origin_city': origin['city'],
            'destination_code': destination_iata.upper(),
            'destination_name': destination['name'],
            'destination_city': destination['city'],
            'distance_km': distance
        }
    
    def add_airport(self, iata_code, latitude, longitude, name, city, country):
        """
        Add a new airport to the database
        """
        self.airports[iata_code.upper()] = (latitude, longitude, name, city, country)
        print(f"✓ Added airport: {iata_code} - {name}")
    
    def process_flight_data(self, flights_data):
        """
        Process a list of flights and calculate distances.
        
        Input format: list of dicts with 'origin' and 'destination' keys
        Example: [
            {'trip_id': 'TR123', 'origin': 'ABJ', 'destination': 'LOS', 'date': '17/Jul/2025'},
            ...
        ]
        
        Returns: DataFrame with distances
        """
        results = []
        
        for flight in flights_data:
            try:
                origin = flight.get('origin', '').strip()
                destination = flight.get('destination', '').strip()
                
                # Extract IATA code if in format "City[CODE]"
                if '[' in origin and ']' in origin:
                    origin = origin[origin.find('[')+1:origin.find(']')]
                if '[' in destination and ']' in destination:
                    destination = destination[destination.find('[')+1:destination.find(']')]
                
                distance_info = self.calculate_distance(origin, destination)
                
                # Combine original data with distance calculation
                result = {**flight, **distance_info}
                results.append(result)
                
                print(f"✓ {origin} → {destination}: {distance_info['distance_km']} km")
                
            except Exception as e:
                print(f"✗ Error processing {flight}: {e}")
                result = {**flight, 'error': str(e)}
                results.append(result)
        
        return pd.DataFrame(results)


# Example usage
if __name__ == "__main__":
    import sys
    
    # Initialize calculator
    calc = FlightDistanceCalculator()
    
    # Read your CSV file
    csv_file = '2ndround.csv'  # ← Change this to your CSV filename
    
    try:
        df = pd.read_csv(csv_file)
        
        # Check if required columns exist
        if 'origin' not in df.columns or 'destination' not in df.columns:
            print("Error: CSV must have 'origin' and 'destination' columns")
            print(f"   Found columns: {', '.join(df.columns)}")
            sys.exit(1)
        
        # Convert to list of dicts
        flights = df.to_dict('records')  
        results_df = calc.process_flight_data(flights)
        
        # Display results
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        
        # Show available columns
        display_cols = ['origin_code', 'destination_code', 'distance_km']
        if 'error' in results_df.columns:
            display_cols.append('error')
        
        available_cols = [col for col in display_cols if col in results_df.columns]
        print(results_df[available_cols].to_string(index=False))
        
        # Save to CSV
        output_file = csv_file.replace('.csv', '_distances.csv')
        results_df.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found!")
        print("   Make sure the CSV file is in the same folder as this script.")
    except Exception as e:
        print(f"Error: {e}")