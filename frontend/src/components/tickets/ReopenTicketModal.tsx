import React, { useState } from 'react';
import { X, RotateCcw } from 'lucide-react';
import { Ticket } from '../../services/ticketsService';

interface ReopenTicketModalProps {
  ticket: Ticket;
  isOpen: boolean;
  onClose: () => void;
  onReopen: (reason: string) => Promise<void>;
}

const ReopenTicketModal: React.FC<ReopenTicketModalProps> = ({
  ticket,
  isOpen,
  onClose,
  onReopen
}) => {
  const [reopenReason, setReopenReason] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!reopenReason.trim()) {
      setError('La razón para reabrir es obligatoria');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      
      await onReopen(reopenReason.trim());
      
      // Reset form and close modal
      setReopenReason('');
      onClose();
      
    } catch (err: any) {
      console.error('Error reopening ticket:', err);
      setError(err.message || 'Error al reabrir el ticket');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      setReopenReason('');
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <RotateCcw className="w-6 h-6 text-orange-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Reabrir Ticket
            </h2>
          </div>
          <button
            onClick={handleClose}
            disabled={submitting}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Ticket Info */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-900">
              {ticket.ticket_number}
            </div>
            <div className="text-sm text-gray-600 truncate">
              {ticket.subject}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Estado actual: <span className="font-medium">Resuelto</span>
            </div>
          </div>

          {/* Reopen Reason */}
          <div className="mb-4">
            <label htmlFor="reopenReason" className="block text-sm font-medium text-gray-700 mb-2">
              Razón para Reabrir *
            </label>
            <textarea
              id="reopenReason"
              value={reopenReason}
              onChange={(e) => setReopenReason(e.target.value)}
              placeholder="Explica por qué necesitas reabrir este ticket..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
              disabled={submitting}
              required
            />
            <div className="text-xs text-gray-500 mt-1">
              Ej: "El cliente reporta que el problema persiste" o "Nueva información disponible"
            </div>
          </div>

          {/* Warning */}
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="text-sm text-yellow-800">
              <strong>Nota:</strong> Al reabrir el ticket, se cambiará el estado a "Reabierto" y se agregará un comentario con la razón.
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="text-sm text-red-600">{error}</div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={submitting}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting || !reopenReason.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              {submitting ? 'Reabriendo...' : 'Reabrir Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReopenTicketModal;
