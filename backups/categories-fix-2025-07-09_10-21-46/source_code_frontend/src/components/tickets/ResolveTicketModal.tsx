import React, { useState } from 'react';
import { X, CheckCircle } from 'lucide-react';
import { Ticket } from '../../services/ticketsService';

interface ResolveTicketModalProps {
  ticket: Ticket;
  isOpen: boolean;
  onClose: () => void;
  onResolve: (resolutionNotes: string) => Promise<void>;
}

const ResolveTicketModal: React.FC<ResolveTicketModalProps> = ({
  ticket,
  isOpen,
  onClose,
  onResolve
}) => {
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!resolutionNotes.trim()) {
      setError('Las notas de resolución son obligatorias');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      
      await onResolve(resolutionNotes.trim());
      
      // Reset form and close modal
      setResolutionNotes('');
      onClose();
      
    } catch (err: unknown) {
      console.error('Error resolving ticket:', err);
      setError(err instanceof Error ? err.message : 'Error al resolver el ticket');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      setResolutionNotes('');
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
            <CheckCircle className="w-6 h-6 text-green-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Resolver Ticket
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
          </div>

          {/* Resolution Notes */}
          <div className="mb-4">
            <label htmlFor="resolutionNotes" className="block text-sm font-medium text-gray-700 mb-2">
              Notas de Resolución *
            </label>
            <textarea
              id="resolutionNotes"
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              placeholder="Describe cómo se resolvió el ticket..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
              disabled={submitting}
              required
            />
            <div className="text-xs text-gray-500 mt-1">
              Explica brevemente cómo se solucionó el problema
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
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting || !resolutionNotes.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              {submitting ? 'Resolviendo...' : 'Resolver Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ResolveTicketModal;
