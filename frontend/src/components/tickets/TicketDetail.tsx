import React, { useState, useEffect } from 'react';
import { X, Edit, UserPlus, MessageSquare, Clock, User, Send } from 'lucide-react';
import { Ticket, TicketComment, ticketsService } from '../../services/ticketsService';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import ResolveTicketModal from './ResolveTicketModal';
import ReopenTicketModal from './ReopenTicketModal';
import TicketConversation from './TicketConversation';
import TicketResolution from './TicketResolution';

interface TicketDetailProps {
  ticketId: string;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: (ticket: Ticket) => void;
  onAssign?: (ticket: Ticket) => void;
}

const TicketDetail: React.FC<TicketDetailProps> = ({
  ticketId,
  isOpen,
  onClose,
  onEdit,
  onAssign
}) => {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<TicketComment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newComment, setNewComment] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [showReopenModal, setShowReopenModal] = useState(false);

  // Load ticket data
  useEffect(() => {
    if (isOpen && ticketId) {
      loadTicketData();
    }
  }, [isOpen, ticketId]);

  const loadTicketData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [ticketData, commentsData] = await Promise.all([
        ticketsService.getTicketById(ticketId),
        ticketsService.getTicketComments(ticketId)
      ]);
      
      setTicket(ticketData);
      setComments(commentsData);
    } catch (err: any) {
      console.error('Error loading ticket data:', err);
      setError(err.response?.data?.message || 'Error al cargar el ticket');
    } finally {
      setLoading(false);
    }
  };

  // Add comment
  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newComment.trim()) return;

    try {
      setSubmittingComment(true);
      setError(null);

      const response = await ticketsService.addTicketComment(ticketId, newComment.trim(), isInternal);

      // Handle API response structure
      if (response.success && response.data) {
        // Create comment object with proper structure for UI
        const newCommentObj = {
          comment_id: response.data.comment_id,
          content: response.data.comment_text || newComment.trim(),
          user_name: 'Tú', // Current user
          user_role: 'current',
          is_internal: isInternal,
          created_at: response.data.created_at || new Date().toISOString(),
          updated_at: response.data.created_at || new Date().toISOString()
        };

        // RELOAD THE ENTIRE PAGE - no more reactive bullshit
        window.location.reload();
      } else {
        throw new Error(response.error || 'Error al agregar comentario');
      }
    } catch (err: any) {
      console.error('Error adding comment:', err);
      setError(err.response?.data?.error || err.message || 'Error al agregar comentario');
    } finally {
      setSubmittingComment(false);
    }
  };

  // Handle status change with page reload
  const handleStatusChange = async (newStatus: string) => {
    if (!ticket) return;

    // Special handling for resolve and reopen status
    if (newStatus === 'resuelto') {
      setShowResolveModal(true);
      return;
    }

    if (newStatus === 'reabierto') {
      setShowReopenModal(true);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await ticketsService.updateTicketStatus(ticketId, newStatus);

      if (response.success) {
        // RELOAD THE ENTIRE PAGE - no more SPA bullshit
        window.location.reload();
      } else {
        throw new Error(response.message || 'Error al cambiar estado del ticket');
      }
    } catch (err: any) {
      console.error('Error updating ticket status:', err);
      const errorMessage = err.response?.data?.error || err.response?.data?.details?.status || err.message || 'Error al cambiar estado del ticket';
      setError(errorMessage);
      setLoading(false);
    }
  };

  // Handle resolve ticket with notes
  const handleResolveTicket = async (resolutionNotes: string) => {
    if (!ticket) return;

    try {
      setLoading(true);
      setError(null);

      const response = await ticketsService.updateTicketStatus(ticketId, 'resuelto', resolutionNotes);

      if (response.success) {
        // RELOAD THE ENTIRE PAGE
        window.location.reload();
      } else {
        throw new Error(response.message || 'Error al resolver el ticket');
      }
    } catch (err: any) {
      console.error('Error resolving ticket:', err);
      const errorMessage = err.response?.data?.error || err.response?.data?.details?.resolution_notes || err.message || 'Error al resolver el ticket';
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Handle reopen ticket with reason
  const handleReopenTicket = async (reason: string) => {
    if (!ticket) return;

    try {
      setLoading(true);
      setError(null);

      // Add comment with reopen reason first
      await ticketsService.addTicketComment(ticketId, `TICKET REABIERTO: ${reason}`, false);

      // Then change status
      const response = await ticketsService.updateTicketStatus(ticketId, 'reabierto');

      if (response.success) {
        // RELOAD THE ENTIRE PAGE
        window.location.reload();
      } else {
        throw new Error(response.message || 'Error al reabrir el ticket');
      }
    } catch (err: any) {
      console.error('Error reopening ticket:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Error al reabrir el ticket';
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critica': return 'bg-red-100 text-red-800 border-red-200';
      case 'alta': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'media': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'baja': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'nuevo': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'asignado': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'en_proceso': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'espera_cliente': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'resuelto': return 'bg-green-100 text-green-800 border-green-200';
      case 'reabierto': return 'bg-red-100 text-red-800 border-red-200';
      case 'cerrado': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'cancelado': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Format status text
  const formatStatus = (status: string) => {
    const statusMap: { [key: string]: string } = {
      'nuevo': 'Nuevo',
      'asignado': 'Asignado',
      'en_proceso': 'En Proceso',
      'espera_cliente': 'Espera Cliente',
      'resuelto': 'Resuelto',
      'cerrado': 'Cerrado',
      'cancelado': 'Cancelado',
      'pendiente_aprobacion': 'Pendiente Aprobación',
      'reabierto': 'Reabierto'
    };
    return statusMap[status] || status;
  };

  // Format priority text
  const formatPriority = (priority: string) => {
    const priorityMap: { [key: string]: string } = {
      'baja': 'Baja',
      'media': 'Media',
      'alta': 'Alta',
      'critica': 'Crítica'
    };
    return priorityMap[priority] || priority;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {ticket ? `Ticket ${ticket.ticket_number}` : 'Cargando...'}
            </h2>
            {ticket && (
              <div className="flex gap-2">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getStatusColor(ticket.status)}`}>
                  {formatStatus(ticket.status)}
                </span>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getPriorityColor(ticket.priority)}`}>
                  {formatPriority(ticket.priority)}
                </span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            {ticket && onEdit && (
              <button
                onClick={() => onEdit(ticket)}
                className="text-blue-600 hover:text-blue-800 p-2 rounded-lg hover:bg-blue-50 transition-colors"
                title="Editar ticket"
              >
                <Edit className="w-5 h-5" />
              </button>
            )}
            {ticket && onAssign && !ticket.assigned_to && (
              <button
                onClick={() => onAssign(ticket)}
                className="text-green-600 hover:text-green-800 p-2 rounded-lg hover:bg-green-50 transition-colors"
                title="Asignar ticket"
              >
                <UserPlus className="w-5 h-5" />
              </button>
            )}

            {/* Status Change Buttons - Flujo Completo */}
            <div className="flex flex-wrap gap-2">
              {/* Nuevo → Asignado o En Proceso */}
              {ticket && ticket.status === 'nuevo' && (
                <>
                  {!ticket.assigned_to && (
                    <button
                      onClick={() => handleStatusChange('asignado')}
                      className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-purple-600 hover:bg-purple-700 transition-colors"
                      title="Asignar ticket"
                    >
                      Asignar
                    </button>
                  )}
                  <button
                    onClick={() => handleStatusChange('en_proceso')}
                    className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                    title="Iniciar trabajo en el ticket"
                  >
                    Iniciar
                  </button>
                </>
              )}

              {/* Asignado → En Proceso */}
              {ticket && ticket.status === 'asignado' && (
                <button
                  onClick={() => handleStatusChange('en_proceso')}
                  className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                  title="Iniciar trabajo en el ticket"
                >
                  Iniciar
                </button>
              )}

              {/* En Proceso → Espera Cliente o Resuelto */}
              {ticket && ticket.status === 'en_proceso' && (
                <>
                  <button
                    onClick={() => handleStatusChange('espera_cliente')}
                    className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-yellow-600 hover:bg-yellow-700 transition-colors"
                    title="Marcar como esperando respuesta del cliente"
                  >
                    Esperar Cliente
                  </button>
                  <button
                    onClick={() => handleStatusChange('resuelto')}
                    className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-green-600 hover:bg-green-700 transition-colors"
                    title="Marcar como resuelto"
                  >
                    Resolver
                  </button>
                </>
              )}

              {/* Espera Cliente → En Proceso o Resuelto */}
              {ticket && ticket.status === 'espera_cliente' && (
                <>
                  <button
                    onClick={() => handleStatusChange('en_proceso')}
                    className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                    title="Continuar trabajo en el ticket"
                  >
                    Continuar
                  </button>
                  <button
                    onClick={() => handleStatusChange('resuelto')}
                    className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-green-600 hover:bg-green-700 transition-colors"
                    title="Marcar como resuelto"
                  >
                    Resolver
                  </button>
                </>
              )}

              {/* Resuelto → Cerrado o Reabierto */}
              {ticket && ticket.status === 'resuelto' && (
                <>
                  <button
                    onClick={() => handleStatusChange('cerrado')}
                    className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-gray-600 hover:bg-gray-700 transition-colors"
                    title="Cerrar ticket definitivamente"
                  >
                    Cerrar
                  </button>
                  <button
                    onClick={() => handleStatusChange('reabierto')}
                    className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-orange-600 hover:bg-orange-700 transition-colors"
                    title="Reabrir ticket por nueva información"
                  >
                    Reabrir
                  </button>
                </>
              )}

              {/* Reabierto → En Proceso */}
              {ticket && ticket.status === 'reabierto' && (
                <button
                  onClick={() => handleStatusChange('en_proceso')}
                  className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                  title="Continuar trabajo en el ticket reabierto"
                >
                  Continuar
                </button>
              )}

              {/* Cerrado - Sin acciones (solo superadmin puede reabrir) */}
              {ticket && ticket.status === 'cerrado' && (
                <span className="inline-flex items-center px-3 py-1 text-xs font-medium rounded-full text-gray-500 bg-gray-100">
                  Ticket Cerrado
                </span>
              )}
            </div>

            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-2 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : error ? (
            <div className="flex-1 p-6">
              <ErrorMessage message={error} />
            </div>
          ) : ticket ? (
            <>
              {/* Left Panel - Ticket Details */}
              <div className="w-1/2 border-r border-gray-200 overflow-y-auto">
                <div className="p-6 space-y-6">
                  {/* Basic Info */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Información del Ticket</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Asunto</label>
                        <p className="text-gray-900">{ticket.subject}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Descripción</label>
                        <p className="text-gray-900 whitespace-pre-wrap">{ticket.description}</p>
                      </div>
                    </div>
                  </div>

                  {/* Client and Site Info */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Cliente y Ubicación</h3>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4 text-gray-400" />
                        <div>
                          <label className="text-sm font-medium text-gray-500">Cliente</label>
                          <p className="text-gray-900">{ticket.client_name}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <div>
                          <label className="text-sm font-medium text-gray-500">Sitio</label>
                          <p className="text-gray-900">{ticket.site_name}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Affected Person */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Persona Afectada</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Nombre</label>
                        <p className="text-gray-900">{ticket.affected_person}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Contacto</label>
                        <p className="text-gray-900">{ticket.affected_person_contact}</p>
                      </div>
                    </div>
                  </div>

                  {/* Assignment and Dates */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Asignación y Fechas</h3>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Creado por</label>
                        <p className="text-gray-900">{ticket.created_by_name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Asignado a</label>
                        <p className="text-gray-900">
                          {ticket.assigned_to_name || (
                            <span className="text-gray-400 italic">Sin asignar</span>
                          )}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <div>
                          <label className="text-sm font-medium text-gray-500">Creado</label>
                          <p className="text-gray-900">
                            {new Date(ticket.created_at).toLocaleString('es-ES')}
                          </p>
                        </div>
                      </div>
                      {ticket.assigned_at && (
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <div>
                            <label className="text-sm font-medium text-gray-500">Asignado</label>
                            <p className="text-gray-900">
                              {new Date(ticket.assigned_at).toLocaleString('es-ES')}
                            </p>
                          </div>
                        </div>
                      )}
                      {ticket.resolved_at && (
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <div>
                            <label className="text-sm font-medium text-gray-500">Resuelto</label>
                            <p className="text-gray-900">
                              {new Date(ticket.resolved_at).toLocaleString('es-ES')}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Resolution Notes */}
                  {ticket.resolution_notes && (
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Resolución</h3>
                      <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                        <p className="text-gray-900 whitespace-pre-wrap">{ticket.resolution_notes}</p>
                      </div>
                    </div>
                  )}

                  {/* Additional Emails */}
                  {ticket.additional_emails && ticket.additional_emails.length > 0 && (
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Correos Adicionales</h3>
                      <div className="space-y-1">
                        {ticket.additional_emails.map((email, index) => (
                          <p key={index} className="text-gray-900">{email}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Panel - Comments */}
              <div className="w-1/2 flex flex-col">
                <div className="p-6 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    Comentarios ({comments.length})
                  </h3>
                </div>

                {/* Threaded Conversation */}
                <div className="flex-1 overflow-y-auto p-6">
                  <TicketConversation
                    comments={comments}
                    loading={loading}
                  />
                </div>

                {/* Add Comment Form */}
                <div className="p-6 border-t border-gray-200">
                  <form onSubmit={handleAddComment} className="space-y-4">
                    <div>
                      <textarea
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Agregar un comentario..."
                      />
                    </div>
                    <div className="flex justify-between items-center">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={isInternal}
                          onChange={(e) => setIsInternal(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">Comentario interno</span>
                      </label>
                      <button
                        type="submit"
                        disabled={!newComment.trim() || submittingComment}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {submittingComment ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                        Enviar
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Resolution Section */}
        {ticket && (
          <TicketResolution ticket={ticket} />
        )}
      </div>

      {/* Resolve Ticket Modal */}
      {ticket && (
        <ResolveTicketModal
          ticket={ticket}
          isOpen={showResolveModal}
          onClose={() => setShowResolveModal(false)}
          onResolve={handleResolveTicket}
        />
      )}

      {/* Reopen Ticket Modal */}
      {ticket && (
        <ReopenTicketModal
          ticket={ticket}
          isOpen={showReopenModal}
          onClose={() => setShowReopenModal(false)}
          onReopen={handleReopenTicket}
        />
      )}
    </div>
  );
};

export default TicketDetail;
