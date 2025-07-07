import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search } from 'lucide-react';

interface State {
  code: string;
  name: string;
}

interface StateSelectorProps {
  country: string;
  value: string;
  onChange: (state: string) => void;
  className?: string;
  error?: boolean;
}

const mexicanStates: State[] = [
  { code: 'AGS', name: 'Aguascalientes' },
  { code: 'BC', name: 'Baja California' },
  { code: 'BCS', name: 'Baja California Sur' },
  { code: 'CAM', name: 'Campeche' },
  { code: 'CHIS', name: 'Chiapas' },
  { code: 'CHIH', name: 'Chihuahua' },
  { code: 'CDMX', name: 'Ciudad de México' },
  { code: 'COAH', name: 'Coahuila' },
  { code: 'COL', name: 'Colima' },
  { code: 'DGO', name: 'Durango' },
  { code: 'GTO', name: 'Guanajuato' },
  { code: 'GRO', name: 'Guerrero' },
  { code: 'HGO', name: 'Hidalgo' },
  { code: 'JAL', name: 'Jalisco' },
  { code: 'MEX', name: 'Estado de México' },
  { code: 'MICH', name: 'Michoacán' },
  { code: 'MOR', name: 'Morelos' },
  { code: 'NAY', name: 'Nayarit' },
  { code: 'NL', name: 'Nuevo León' },
  { code: 'OAX', name: 'Oaxaca' },
  { code: 'PUE', name: 'Puebla' },
  { code: 'QRO', name: 'Querétaro' },
  { code: 'QROO', name: 'Quintana Roo' },
  { code: 'SLP', name: 'San Luis Potosí' },
  { code: 'SIN', name: 'Sinaloa' },
  { code: 'SON', name: 'Sonora' },
  { code: 'TAB', name: 'Tabasco' },
  { code: 'TAMPS', name: 'Tamaulipas' },
  { code: 'TLAX', name: 'Tlaxcala' },
  { code: 'VER', name: 'Veracruz' },
  { code: 'YUC', name: 'Yucatán' },
  { code: 'ZAC', name: 'Zacatecas' }
];

const StateSelector: React.FC<StateSelectorProps> = ({ 
  country,
  value, 
  onChange, 
  className = '', 
  error = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredStates, setFilteredStates] = useState<State[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Determine if we should show Mexican states or a simple input
  const isMexico = country === 'México';

  useEffect(() => {
    if (isMexico) {
      const filtered = mexicanStates.filter(state =>
        state.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        state.code.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredStates(filtered);
    }
  }, [searchTerm, isMexico]);

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

  // Auto-select "N/A" for non-Mexican countries
  useEffect(() => {
    if (!isMexico && value !== 'N/A') {
      onChange('N/A');
    }
  }, [country, isMexico, value, onChange]);

  const selectedState = mexicanStates.find(state => state.name === value || state.code === value);

  const handleSelect = (state: State) => {
    onChange(state.name);
    setIsOpen(false);
    setSearchTerm('');
  };

  // For non-Mexican countries, show a disabled input with "N/A"
  if (!isMexico) {
    return (
      <input
        type="text"
        value="N/A"
        readOnly
        className={`w-full px-3 py-2 border rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed ${
          error ? 'border-red-500' : 'border-gray-300'
        } ${className}`}
        placeholder="No aplica para este país"
      />
    );
  }

  // For Mexico, show the dropdown selector
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
          {selectedState ? (
            <>
              <span className="mr-2 text-xs text-gray-500">{selectedState.code}</span>
              <span>{selectedState.name}</span>
            </>
          ) : (
            <span className="text-gray-500">Seleccionar estado</span>
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
                placeholder="Buscar estado..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
            </div>
          </div>
          <div className="max-h-48 overflow-y-auto">
            {filteredStates.length === 0 ? (
              <div className="px-4 py-3 text-gray-500 text-center">
                No se encontraron estados
              </div>
            ) : (
              filteredStates.map((state) => (
                <button
                  key={state.code}
                  type="button"
                  onClick={() => handleSelect(state)}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center ${
                    selectedState?.code === state.code ? 'bg-blue-50 text-blue-600' : ''
                  }`}
                >
                  <span className="mr-3 text-xs text-gray-500 w-12">{state.code}</span>
                  <span>{state.name}</span>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StateSelector;
