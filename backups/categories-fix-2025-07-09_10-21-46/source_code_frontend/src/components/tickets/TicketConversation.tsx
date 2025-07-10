import React from 'react';
import { MessageSquare, User, Clock, Eye, EyeOff } from 'lucide-react';
import { TicketComment } from '../../services/ticketsService';

interface TicketConversationProps {
  comments: TicketComment[];
  loading?: boolean;
}

const TicketConversation: React.FC<TicketConversationProps> = ({
  comments,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="flex space-x-3">
              <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-300 rounded w-1/4"></div>
                <div className="h-16 bg-gray-300 rounded"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (comments.length === 0) {
    return (
      <div className="text-center py-8">
        <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No hay comentarios aún</p>
        <p className="text-sm text-gray-400">Sé el primero en agregar un comentario</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {comments.map((comment, index) => (
        <div key={comment.comment_id} className="relative">
          {/* Thread line for all but last comment */}
          {index < comments.length - 1 && (
            <div className="absolute left-4 top-12 bottom-0 w-0.5 bg-gray-200"></div>
          )}
          
          {/* Comment */}
          <div className="flex space-x-3">
            {/* Avatar */}
            <div className="flex-shrink-0">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                comment.is_internal 
                  ? 'bg-orange-500' 
                  : comment.user_role === 'client' || comment.user_role === 'solicitante'
                    ? 'bg-blue-500'
                    : 'bg-green-500'
              }`}>
                <User className="w-4 h-4" />
              </div>
            </div>

            {/* Comment Content */}
            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">
                    {comment.user_name || 'Usuario'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {comment.user_role === 'client' || comment.user_role === 'solicitante' ? 'Cliente' : 'Técnico'}
                  </span>
                  {comment.is_internal && (
                    <div className="flex items-center space-x-1 text-orange-600">
                      <EyeOff className="w-3 h-3" />
                      <span className="text-xs font-medium">Interno</span>
                    </div>
                  )}
                  {!comment.is_internal && (
                    <div className="flex items-center space-x-1 text-green-600">
                      <Eye className="w-3 h-3" />
                      <span className="text-xs font-medium">Público</span>
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-1 text-gray-400">
                  <Clock className="w-3 h-3" />
                  <span className="text-xs">
                    {new Date(comment.created_at).toLocaleString('es-ES', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>

              {/* Comment Body */}
              <div className={`rounded-lg p-3 ${
                comment.is_internal 
                  ? 'bg-orange-50 border border-orange-200' 
                  : comment.user_role === 'client' || comment.user_role === 'solicitante'
                    ? 'bg-blue-50 border border-blue-200'
                    : 'bg-green-50 border border-green-200'
              }`}>
                <p className="text-sm text-gray-900 whitespace-pre-wrap">
                  {comment.content}
                </p>
              </div>

              {/* Metadata */}
              {comment.updated_at !== comment.created_at && (
                <div className="mt-1 text-xs text-gray-400">
                  Editado: {new Date(comment.updated_at).toLocaleString('es-ES')}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TicketConversation;
