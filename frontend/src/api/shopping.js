import api from './axios.js'

export const shoppingApi = {
  getLists: async () => {
    const res = await api.get('/shopping/')
    return res.data
  },
  createList: async (data) => {
    const res = await api.post('/shopping/', data)
    return res.data
  },
  autoGenerate: async () => {
    const res = await api.post('/shopping/auto-generate')
    return res.data
  },
  addItem: async (listId, data) => {
    const res = await api.post(`/shopping/${listId}/items`, data)
    return res.data
  },
  updateItem: async (itemId, data) => {
    const res = await api.patch(`/shopping/items/${itemId}`, data)
    return res.data
  },
  deleteItem: async (itemId) => {
    await api.delete(`/shopping/items/${itemId}`)
  },
}
