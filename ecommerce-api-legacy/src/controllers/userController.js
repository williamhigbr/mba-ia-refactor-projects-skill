class UserController {
  constructor(userModel) {
    this.userModel = userModel;
  }

  async deleteUser(id) {
    const changes = await this.userModel.deleteById(id);
    if (changes === 0) {
      return { status: 404, body: { error: 'Usuário não encontrado' } };
    }
    return { status: 200, body: { msg: 'Usuário deletado' } };
  }
}

module.exports = UserController;
