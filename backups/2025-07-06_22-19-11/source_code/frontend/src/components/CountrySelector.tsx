import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search } from 'lucide-react';

interface Country {
  code: string;
  name: string;
  flag: string;
}

interface CountrySelectorProps {
  value: string;
  onChange: (country: string) => void;
  className?: string;
  error?: boolean;
}

const countries: Country[] = [
  { code: 'MX', name: 'México', flag: '🇲🇽' },
  { code: 'US', name: 'Estados Unidos', flag: '🇺🇸' },
  { code: 'CA', name: 'Canadá', flag: '🇨🇦' },
  { code: 'ES', name: 'España', flag: '🇪🇸' },
  { code: 'CO', name: 'Colombia', flag: '🇨🇴' },
  { code: 'AR', name: 'Argentina', flag: '🇦🇷' },
  { code: 'CL', name: 'Chile', flag: '🇨🇱' },
  { code: 'PE', name: 'Perú', flag: '🇵🇪' },
  { code: 'BR', name: 'Brasil', flag: '🇧🇷' },
  { code: 'UY', name: 'Uruguay', flag: '🇺🇾' },
  { code: 'PY', name: 'Paraguay', flag: '🇵🇾' },
  { code: 'BO', name: 'Bolivia', flag: '🇧🇴' },
  { code: 'EC', name: 'Ecuador', flag: '🇪🇨' },
  { code: 'VE', name: 'Venezuela', flag: '🇻🇪' },
  { code: 'CR', name: 'Costa Rica', flag: '🇨🇷' },
  { code: 'PA', name: 'Panamá', flag: '🇵🇦' },
  { code: 'GT', name: 'Guatemala', flag: '🇬🇹' },
  { code: 'HN', name: 'Honduras', flag: '🇭🇳' },
  { code: 'SV', name: 'El Salvador', flag: '🇸🇻' },
  { code: 'NI', name: 'Nicaragua', flag: '🇳🇮' },
  { code: 'BZ', name: 'Belice', flag: '🇧🇿' },
  { code: 'CU', name: 'Cuba', flag: '🇨🇺' },
  { code: 'DO', name: 'República Dominicana', flag: '🇩🇴' },
  { code: 'HT', name: 'Haití', flag: '🇭🇹' },
  { code: 'JM', name: 'Jamaica', flag: '🇯🇲' },
  { code: 'TT', name: 'Trinidad y Tobago', flag: '🇹🇹' },
  { code: 'BB', name: 'Barbados', flag: '🇧🇧' },
  { code: 'GD', name: 'Granada', flag: '🇬🇩' },
  { code: 'LC', name: 'Santa Lucía', flag: '🇱🇨' },
  { code: 'VC', name: 'San Vicente y las Granadinas', flag: '🇻🇨' },
  { code: 'AG', name: 'Antigua y Barbuda', flag: '🇦🇬' },
  { code: 'KN', name: 'San Cristóbal y Nieves', flag: '🇰🇳' },
  { code: 'DM', name: 'Dominica', flag: '🇩🇲' },
  { code: 'BS', name: 'Bahamas', flag: '🇧🇸' },
  { code: 'FR', name: 'Francia', flag: '🇫🇷' },
  { code: 'DE', name: 'Alemania', flag: '🇩🇪' },
  { code: 'IT', name: 'Italia', flag: '🇮🇹' },
  { code: 'PT', name: 'Portugal', flag: '🇵🇹' },
  { code: 'GB', name: 'Reino Unido', flag: '🇬🇧' },
  { code: 'IE', name: 'Irlanda', flag: '🇮🇪' },
  { code: 'NL', name: 'Países Bajos', flag: '🇳🇱' },
  { code: 'BE', name: 'Bélgica', flag: '🇧🇪' },
  { code: 'CH', name: 'Suiza', flag: '🇨🇭' },
  { code: 'AT', name: 'Austria', flag: '🇦🇹' },
  { code: 'SE', name: 'Suecia', flag: '🇸🇪' },
  { code: 'NO', name: 'Noruega', flag: '🇳🇴' },
  { code: 'DK', name: 'Dinamarca', flag: '🇩🇰' },
  { code: 'FI', name: 'Finlandia', flag: '🇫🇮' },
  { code: 'IS', name: 'Islandia', flag: '🇮🇸' },
  { code: 'PL', name: 'Polonia', flag: '🇵🇱' },
  { code: 'CZ', name: 'República Checa', flag: '🇨🇿' },
  { code: 'SK', name: 'Eslovaquia', flag: '🇸🇰' },
  { code: 'HU', name: 'Hungría', flag: '🇭🇺' },
  { code: 'RO', name: 'Rumania', flag: '🇷🇴' },
  { code: 'BG', name: 'Bulgaria', flag: '🇧🇬' },
  { code: 'HR', name: 'Croacia', flag: '🇭🇷' },
  { code: 'SI', name: 'Eslovenia', flag: '🇸🇮' },
  { code: 'EE', name: 'Estonia', flag: '🇪🇪' },
  { code: 'LV', name: 'Letonia', flag: '🇱🇻' },
  { code: 'LT', name: 'Lituania', flag: '🇱🇹' },
  { code: 'GR', name: 'Grecia', flag: '🇬🇷' },
  { code: 'CY', name: 'Chipre', flag: '🇨🇾' },
  { code: 'MT', name: 'Malta', flag: '🇲🇹' },
  { code: 'LU', name: 'Luxemburgo', flag: '🇱🇺' },
  { code: 'JP', name: 'Japón', flag: '🇯🇵' },
  { code: 'KR', name: 'Corea del Sur', flag: '🇰🇷' },
  { code: 'CN', name: 'China', flag: '🇨🇳' },
  { code: 'IN', name: 'India', flag: '🇮🇳' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
  { code: 'NZ', name: 'Nueva Zelanda', flag: '🇳🇿' },
  { code: 'SG', name: 'Singapur', flag: '🇸🇬' },
  { code: 'MY', name: 'Malasia', flag: '🇲🇾' },
  { code: 'TH', name: 'Tailandia', flag: '🇹🇭' },
  { code: 'PH', name: 'Filipinas', flag: '🇵🇭' },
  { code: 'ID', name: 'Indonesia', flag: '🇮🇩' },
  { code: 'VN', name: 'Vietnam', flag: '🇻🇳' },
  { code: 'ZA', name: 'Sudáfrica', flag: '🇿🇦' },
  { code: 'EG', name: 'Egipto', flag: '🇪🇬' },
  { code: 'MA', name: 'Marruecos', flag: '🇲🇦' },
  { code: 'NG', name: 'Nigeria', flag: '🇳🇬' },
  { code: 'KE', name: 'Kenia', flag: '🇰🇪' },
  { code: 'GH', name: 'Ghana', flag: '🇬🇭' },
  { code: 'IL', name: 'Israel', flag: '🇮🇱' },
  { code: 'AE', name: 'Emiratos Árabes Unidos', flag: '🇦🇪' },
  { code: 'SA', name: 'Arabia Saudí', flag: '🇸🇦' },
  { code: 'TR', name: 'Turquía', flag: '🇹🇷' },
  { code: 'RU', name: 'Rusia', flag: '🇷🇺' },
  { code: 'UA', name: 'Ucrania', flag: '🇺🇦' }
];

const CountrySelector: React.FC<CountrySelectorProps> = ({ 
  value, 
  onChange, 
  className = '', 
  error = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredCountries, setFilteredCountries] = useState(countries);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const filtered = countries.filter(country =>
      country.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredCountries(filtered);
  }, [searchTerm]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const selectedCountry = countries.find(country => country.name === value);

  const handleSelect = (country: Country) => {
    onChange(country.name);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full px-3 py-2 text-left border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent flex items-center justify-between ${
          error ? 'border-red-500' : 'border-gray-300'
        } ${isOpen ? 'ring-2 ring-blue-500 border-transparent' : ''}`}
      >
        <div className="flex items-center">
          {selectedCountry ? (
            <>
              <span className="mr-2">{selectedCountry.flag}</span>
              <span>{selectedCountry.name}</span>
            </>
          ) : (
            <span className="text-gray-500">Seleccionar país</span>
          )}
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-hidden">
          <div className="p-2 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Buscar país..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
            </div>
          </div>
          <div className="max-h-48 overflow-y-auto">
            {filteredCountries.length === 0 ? (
              <div className="px-4 py-3 text-gray-500 text-center">
                No se encontraron países
              </div>
            ) : (
              filteredCountries.map((country) => (
                <button
                  key={country.code}
                  type="button"
                  onClick={() => handleSelect(country)}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center ${
                    selectedCountry?.code === country.code ? 'bg-blue-50 text-blue-600' : ''
                  }`}
                >
                  <span className="mr-3">{country.flag}</span>
                  <span>{country.name}</span>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CountrySelector;
