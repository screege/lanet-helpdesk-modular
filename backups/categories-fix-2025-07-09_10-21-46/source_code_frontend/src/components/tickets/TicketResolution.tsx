import React from 'react';
import { CheckCircle, Clock, User } from 'lucide-react';
import { Ticket } from '../../services/ticketsService';

interface TicketResolutionProps {
  ticket: Ticket;
}

const TicketResolution: React.FC<TicketResolutionProps> = ({ ticket }) => {
  // Only show if ticket is resolved and has resolution notes
  if (ticket.status !== 'resuelto' && ticket.status !== 'cerrado' && ticket.status !== 'reabierto') {
    return null;
  }

  if (!ticket.resolution_notes) {
    return null;
  }

  return (
    <div className="mt-8 border-t border-gray-200 pt-6">
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-green-900">
              Ticket Resuelto
            </h3>
            <div className="flex items-center space-x-4 text-sm text-green-700">
              {ticket.resolved_at && (
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span>
                    Resuelto el {new Date(ticket.resolved_at).toLocaleString('es-ES', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              )}
              {ticket.assigned_to_name && (
                <div className="flex items-center space-x-1">
                  <User className="w-4 h-4" />
                  <span>por {ticket.assigned_to_name}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Resolution Notes */}
        <div className="bg-white rounded-md p-4 border border-green-300">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Descripción de la Resolución:
          </h4>
          <div className="text-sm text-gray-700 whitespace-pre-wrap">
            {ticket.resolution_notes}
          </div>
        </div>

        {/* Reopened Notice */}
        {ticket.status === 'reabierto' && (
          <div className="mt-4 p-3 bg-orange-100 border border-orange-300 rounded-md">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span className="text-sm font-medium text-orange-800">
                Este ticket fue reabierto después de la resolución
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TicketResolution;
