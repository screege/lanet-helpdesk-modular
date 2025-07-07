import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, User, AlertCircle, Send, CheckCircle, Paperclip, Download } from 'lucide-react';
import { Ticket, TicketComment, TicketAttachment, ticketsService } from '../../services/ticketsService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import ErrorMessage from '../../components/common/ErrorMessage';
import ResolveTicketModal from '../../components/tickets/ResolveTicketModal';
import ReopenTicketModal from '../../components/tickets/ReopenTicketModal';
import { useAuth } from '../../contexts/AuthContext';

const TicketDetailPage: React.FC = () => {
  const { ticketId } = useParams<{ ticketId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<TicketComment[]>([]);
  const [attachments, setAttachments] = useState<TicketAttachment[]>([]);
  const [resolutions, setResolutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newComment, setNewComment] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [showReopenModal, setShowReopenModal] = useState(false);
  const [downloadingAttachments, setDownloadingAttachments] = useState<Set<string>>(new Set());

  // Load ticket data
  useEffect(() => {
    if (ticketId) {
      loadTicketData();
    }
  }, [ticketId]);

  const loadTicketData = async () => {
    if (!ticketId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const [ticketData, commentsData, attachmentsData] = await Promise.all([
        ticketsService.getTicketById(ticketId),
        ticketsService.getTicketComments(ticketId),
        ticketsService.getTicketAttachments(ticketId)
      ]);

      console.log('🔗 Attachments loaded:', attachmentsData);
      setTicket(ticketData);
      setComments(commentsData);
      setAttachments(attachmentsData);

      // Cargar historial de resoluciones
      await loadResolutions();
    } catch (err: any) {
      console.error('Error loading ticket data:', err);
      setError(err.response?.data?.message || 'Error al cargar el ticket');
    } finally {
      setLoading(false);
    }
  };

  const loadResolutions = async () => {
    if (!ticketId) return;

    try {
      console.log('🔍 Loading resolutions for ticket:', ticketId);
      const resolutionsData = await ticketsService.getTicketResolutions(ticketId);
      console.log('✅ Resolutions loaded:', resolutionsData);
      setResolutions(resolutionsData);
    } catch (error) {
      console.error('❌ Error loading resolutions:', error);
    }
  };

  // Add comment
  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newComment.trim() || !ticketId) return;
    
    try {
      setSubmittingComment(true);
      await ticketsService.addTicketComment(ticketId, newComment.trim(), isInternal);
      // RELOAD THE ENTIRE PAGE - no more reactive bullshit
      window.location.reload();
    } catch (err: any) {
      console.error('Error adding comment:', err);
      setError(err.response?.data?.message || 'Error al agregar comentario');
      setSubmittingComment(false);
    }
  };

  // Handle status change with page reload
  const handleStatusChange = async (newStatus: string) => {
    if (!ticket || !ticketId) return;

    // Special handling for resolve and reopen
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
      await ticketsService.updateTicketStatus(ticketId, newStatus);

      // RELOAD THE ENTIRE PAGE
      window.location.reload();
    } catch (err: any) {
      console.error('Error updating ticket status:', err);
      setError(err.response?.data?.message || 'Error al cambiar estado del ticket');
      setLoading(false);
    }
  };

  // Handle resolve with notes
  const handleResolveTicket = async (resolutionNotes: string) => {
    if (!ticket || !ticketId) return;

    try {
      setLoading(true);
      await ticketsService.updateTicketStatus(ticketId, 'resuelto', resolutionNotes);
      window.location.reload();
    } catch (err: any) {
      console.error('Error resolving ticket:', err);
      throw new Error(err.message || 'Error al resolver el ticket');
    }
  };

  // Handle reopen with reason
  const handleReopenTicket = async (reason: string) => {
    if (!ticket || !ticketId) return;

    try {
      setLoading(true);
      // Add comment with reason first
      await ticketsService.addTicketComment(ticketId, `TICKET REABIERTO: ${reason}`, false);
      // Then change status
      await ticketsService.updateTicketStatus(ticketId, 'reabierto');
      window.location.reload();
    } catch (err: any) {
      console.error('Error reopening ticket:', err);
      throw new Error(err.message || 'Error al reabrir el ticket');
    }
  };

  // Handle attachment download
  const handleDownloadAttachment = async (attachmentId: string, originalFilename: string) => {
    // Prevent multiple downloads of the same attachment
    if (downloadingAttachments.has(attachmentId)) {
      console.log('🔽 Download already in progress for:', attachmentId);
      return;
    }

    try {
      console.log('🔽 Downloading attachment:', attachmentId, originalFilename);

      // Mark attachment as downloading
      setDownloadingAttachments(prev => new Set(prev).add(attachmentId));

      // Get the token for authentication (using correct key)
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      // Create download URL
      const downloadUrl = `http://localhost:5001/api/tickets/attachments/${attachmentId}/download`;

      // Fetch the file
      const response = await fetch(downloadUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = originalFilename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log('✅ Download completed successfully');
    } catch (err: any) {
      console.error('❌ Download error:', err);
      setError(`Error al descargar archivo: ${err.message}`);
    } finally {
      // Remove attachment from downloading set
      setDownloadingAttachments(prev => {
        const newSet = new Set(prev);
        newSet.delete(attachmentId);
        return newSet;
      });
    }
  };

  // Cliente reabrir directamente sin modal
  const handleClientReopen = async () => {
    if (!ticket || !ticketId) return;

    try {
      setLoading(true);
      // Add comment explaining why it's not resolved
      await ticketsService.addTicketComment(ticketId, 'El problema no está resuelto. Necesito más ayuda.', false);
      // Then change status
      await ticketsService.updateTicketStatus(ticketId, 'reabierto');
      window.location.reload();
    } catch (err: any) {
      console.error('Error reopening ticket:', err);
      setError(err.response?.data?.message || 'Error al reabrir el ticket');
      setLoading(false);
    }
  };

  // Format functions
  const formatStatus = (status: string) => {
    const statusMap: { [key: string]: string } = {
      'nuevo': 'Nuevo',
      'asignado': 'Asignado',
      'en_proceso': 'En Proceso',
      'espera_cliente': 'Esperando Cliente',
      'resuelto': 'Resuelto',
      'cerrado': 'Cerrado',
      'cancelado': 'Cancelado'
    };
    return statusMap[status] || status;
  };

  const formatPriority = (priority: string) => {
    const priorityMap: { [key: string]: string } = {
      'baja': 'Baja',
      'media': 'Media',
      'alta': 'Alta',
      'critica': 'Crítica'
    };
    return priorityMap[priority] || priority;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'nuevo': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'asignado': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'en_proceso': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'espera_cliente': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'resuelto': return 'bg-green-100 text-green-800 border-green-200';
      case 'cerrado': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'cancelado': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'baja': return 'bg-green-100 text-green-800 border-green-200';
      case 'media': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'alta': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'critica': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => navigate('/tickets')}
              className="inline-flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver a Tickets
            </button>
          </div>
          <ErrorMessage message={error} />
        </div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <button
              onClick={() => navigate('/tickets')}
              className="inline-flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver a Tickets
            </button>
          </div>
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ticket no encontrado</h3>
            <p className="text-gray-500">El ticket solicitado no existe o no tienes permisos para verlo.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/tickets')}
                className="inline-flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Volver a Tickets
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Ticket {ticket.ticket_number}
                </h1>
                <p className="text-gray-500">{ticket.subject}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Status and Priority Badges */}
              <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full border ${getStatusColor(ticket.status)}`}>
                {formatStatus(ticket.status)}
              </span>
              <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full border ${getPriorityColor(ticket.priority)}`}>
                {formatPriority(ticket.priority)}
              </span>
              
              {/* Action Buttons */}
              <button
                onClick={() => navigate(`/tickets/${ticketId}/edit`)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <Edit className="w-4 h-4 mr-2" />
                Editar
              </button>
              
              {/* Status Change Buttons */}
              {/* Iniciar Trabajo - Solo técnicos/admins pueden iniciar trabajo en tickets nuevos o asignados */}
              {(ticket.status === 'nuevo' || ticket.status === 'asignado') && user?.role && ['superadmin', 'technician'].includes(user.role) && (
                <button
                  onClick={() => handleStatusChange('en_proceso')}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Iniciar Trabajo
                </button>
              )}
              
              {ticket.status === 'en_proceso' && (
                <>
                  {/* Solo técnicos/admins pueden cambiar a espera_cliente y resolver */}
                  {user?.role && ['superadmin', 'technician'].includes(user.role) && (
                    <>
                      <button
                        onClick={() => handleStatusChange('espera_cliente')}
                        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-yellow-600 hover:bg-yellow-700"
                      >
                        Esperar Cliente
                      </button>
                      <button
                        onClick={() => handleStatusChange('resuelto')}
                        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                      >
                        Resolver
                      </button>
                    </>
                  )}

                  {/* Clientes pueden cerrar directamente si están satisfechos */}
                  {user?.role && ['client_admin', 'solicitante'].includes(user.role) && (
                    <button
                      onClick={() => handleStatusChange('cerrado')}
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-gray-600 hover:bg-gray-700"
                    >
                      Cerrar (Satisfecho)
                    </button>
                  )}
                </>
              )}
              
              {/* Espera Cliente → Solo técnicos pueden continuar/resolver */}
              {ticket.status === 'espera_cliente' && user?.role && ['superadmin', 'technician'].includes(user.role) && (
                <>
                  <button
                    onClick={() => handleStatusChange('en_proceso')}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Continuar Trabajo
                  </button>
                  <button
                    onClick={() => handleStatusChange('resuelto')}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                  >
                    Resolver
                  </button>
                </>
              )}

              {ticket.status === 'resuelto' && (
                <>
                  {/* Cualquiera puede cerrar un ticket resuelto */}
                  <button
                    onClick={() => handleStatusChange('cerrado')}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-gray-600 hover:bg-gray-700"
                  >
                    {user?.role && ['client_admin', 'solicitante'].includes(user.role)
                      ? 'Confirmar Resolución'
                      : 'Cerrar Ticket'}
                  </button>

                  {/* Solo técnicos/admins pueden reabrir directamente */}
                  {user?.role && ['superadmin', 'technician'].includes(user.role) && (
                    <button
                      onClick={() => handleStatusChange('reabierto')}
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
                    >
                      Reabrir
                    </button>
                  )}

                  {/* Clientes pueden reabrir directamente */}
                  {user?.role && ['client_admin', 'solicitante'].includes(user.role) && (
                    <button
                      onClick={() => handleClientReopen()}
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
                    >
                      No Resuelto
                    </button>
                  )}
                </>
              )}

              {/* Reabierto → Solo técnicos pueden continuar */}
              {ticket.status === 'reabierto' && user?.role && ['superadmin', 'technician'].includes(user.role) && (
                <button
                  onClick={() => handleStatusChange('en_proceso')}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Retomar Trabajo
                </button>
              )}

              {/* Cerrado → Reabrir */}
              {ticket.status === 'cerrado' && (
                <button
                  onClick={() => handleStatusChange('reabierto')}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700"
                >
                  Reabrir Ticket
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Ticket Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Ticket Information */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Información del Ticket</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Descripción</label>
                  <p className="mt-1 text-gray-900">{ticket.description}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Persona Afectada</label>
                  <p className="mt-1 text-gray-900">{ticket.affected_person}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Contacto</label>
                  <p className="mt-1 text-gray-900">{ticket.affected_person_contact}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Canal</label>
                  <p className="mt-1 text-gray-900">
                    {ticket.channel === 'email' && '📧 Email'}
                    {ticket.channel === 'portal' && '🌐 Portal'}
                    {ticket.channel === 'phone' && '📞 Teléfono'}
                  </p>
                </div>
              </div>
            </div>

            {/* Attachments Section */}
            {attachments.length > 0 && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <Paperclip className="w-5 h-5" />
                  Archivos Adjuntos ({attachments.length})
                </h2>
                <div className="space-y-3">
                  {attachments.map((attachment) => (
                    <div key={attachment.attachment_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Paperclip className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{attachment.original_filename}</p>
                          <p className="text-xs text-gray-500">
                            {attachment.file_size_display} • Subido por {attachment.uploaded_by_name} • {new Date(attachment.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <button
                        className={`flex items-center gap-2 px-3 py-2 text-sm rounded-md transition-colors ${
                          downloadingAttachments.has(attachment.attachment_id)
                            ? 'text-gray-400 cursor-not-allowed'
                            : 'text-blue-600 hover:text-blue-800 hover:bg-blue-50'
                        }`}
                        onClick={() => handleDownloadAttachment(attachment.attachment_id, attachment.original_filename)}
                        disabled={downloadingAttachments.has(attachment.attachment_id)}
                      >
                        <Download className="w-4 h-4" />
                        {downloadingAttachments.has(attachment.attachment_id) ? 'Descargando...' : 'Descargar'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Comments/Communication Thread - DISEÑO ORIGINAL */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Conversación</h3>
                <span className="text-sm text-gray-500">{comments.length} comentarios</span>
              </div>

              {/* Comments List - DISEÑO ORIGINAL INCREÍBLE */}
              <div className="px-6 py-4 space-y-4 max-h-96 overflow-y-auto">
                {comments.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">💬</div>
                    <p>No hay comentarios aún</p>
                    <p className="text-sm">Sé el primero en agregar un comentario</p>
                  </div>
                ) : (
                  comments.map((comment) => {
                    // Distinción de colores por tipo y rol
                    let borderColor = 'border-blue-400';
                    let bgColor = 'bg-blue-50';

                    if (comment.is_internal) {
                      borderColor = 'border-yellow-400';
                      bgColor = 'bg-yellow-50';
                    } else if (comment.user_role === 'superadmin' || comment.user_role === 'technician') {
                      borderColor = 'border-green-400';
                      bgColor = 'bg-green-50';
                    } else if (comment.user_role === 'client_admin' || comment.user_role === 'solicitante') {
                      borderColor = 'border-blue-400';
                      bgColor = 'bg-blue-50';
                    }

                    return (
                    <div key={comment.comment_id} className={`border-l-4 pl-4 py-3 ${borderColor} ${bgColor}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center">
                            <User className="h-4 w-4 text-gray-400 mr-1" />
                            <span className="text-sm font-medium text-gray-900">{comment.user_name}</span>
                          </div>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-500">
                            {new Date(comment.created_at).toLocaleString('es-ES')}
                          </span>
                          {comment.is_internal && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                              Nota Interna
                            </span>
                          )}
                          {!comment.is_internal && (
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              comment.user_role === 'superadmin' || comment.user_role === 'technician'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}>
                              {comment.user_role === 'superadmin' ? 'Admin' :
                               comment.user_role === 'technician' ? 'Técnico' :
                               comment.user_role === 'client_admin' ? 'Cliente Admin' :
                               comment.user_role === 'solicitante' ? 'Solicitante' : 'Usuario'}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-gray-900 whitespace-pre-wrap">{comment.content}</p>
                      </div>
                    </div>
                    );
                  })
                )}
              </div>

              {/* Add Comment Form */}
              <form onSubmit={handleAddComment} className="border-t pt-4">
                <div className="mb-4">
                  {/* Internal comment checkbox - only visible to superadmin and technician */}
                  {user?.role && ['superadmin', 'technician'].includes(user.role) && (
                    <label className="flex items-center gap-2 mb-2">
                      <input
                        type="checkbox"
                        checked={isInternal}
                        onChange={(e) => setIsInternal(e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">Comentario interno (solo visible para técnicos)</span>
                    </label>
                  )}
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Escribe tu comentario..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={!newComment.trim() || submittingComment}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-4 h-4 mr-2" />
                    {submittingComment ? 'Enviando...' : 'Enviar Comentario'}
                  </button>
                </div>
              </form>
            </div>

            {/* Resolution History - HISTORIAL REAL COMPLETO */}
            {console.log('🎯 Rendering resolutions check:', resolutions.length, resolutions)}
            {resolutions.length > 0 && (
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">Historial de Resoluciones</h3>
                  <span className="text-sm text-gray-500">
                    {resolutions.length} resoluciones
                  </span>
                </div>
                <div className="px-6 py-4 space-y-4">
                  {resolutions.map((resolution, index) => (
                    <div key={resolution.resolution_id} className="border-l-4 border-green-400 bg-green-50 pl-4 py-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center">
                            <CheckCircle className="h-4 w-4 text-green-600 mr-1" />
                            <span className="text-sm font-medium text-green-900">
                              {resolution.resolved_by_name || 'Sistema'}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-500">
                            {new Date(resolution.resolved_at).toLocaleString('es-ES')}
                          </span>
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                            Resolución #{resolutions.length - index}
                          </span>
                        </div>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-green-900 whitespace-pre-wrap">{resolution.resolution_notes}</p>
                      </div>
                    </div>
                  ))}

                  {ticket?.status === 'reabierto' && (
                    <div className="mt-4 p-3 bg-orange-100 border border-orange-300 rounded text-sm text-orange-800">
                      ⚠️ Este ticket fue reabierto después de la resolución más reciente
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6">
            {/* Ticket Metadata */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Detalles</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-500">Creado</label>
                  <p className="text-gray-900">{new Date(ticket.created_at).toLocaleString()}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Actualizado</label>
                  <p className="text-gray-900">{new Date(ticket.updated_at).toLocaleString()}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Asignado a</label>
                  <p className="text-gray-900">{ticket.assigned_to_name || 'Sin asignar'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Cliente</label>
                  <p className="text-gray-900">{ticket.client_name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Sitio</label>
                  <p className="text-gray-900">{ticket.site_name}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {ticket && (
        <>
          <ResolveTicketModal
            ticket={ticket}
            isOpen={showResolveModal}
            onClose={() => setShowResolveModal(false)}
            onResolve={handleResolveTicket}
          />
          <ReopenTicketModal
            ticket={ticket}
            isOpen={showReopenModal}
            onClose={() => setShowReopenModal(false)}
            onReopen={handleReopenTicket}
          />
        </>
      )}
    </div>
  );
};

export default TicketDetailPage;
